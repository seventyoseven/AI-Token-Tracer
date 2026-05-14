# ai_token_tracker/models/ai_token_tracker_api_key.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes

# AES block size
BLOCK_SIZE = 16

class AiApiKey(models.Model):
    _name = 'ai_token_tracker.api_key'
    _description = 'AI API Key Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Key Name / Purpose', required=True, tracking=True)
      
    # This field stores the base64-encoded *encrypted* key
    key_value = fields.Text(string='API Key')
      
    user_id = fields.Many2one(
        'res.users', 
        string='Key Owner', 
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
      
    subscription_id = fields.Many2one(
        'ai_token_tracker.subscription', 
        string='Subscription',
        required=True,
        ondelete='cascade'
    )
      
    provider_id = fields.Many2one(
        related='subscription_id.provider_id', 
        store=True, 
        readonly=True
    )
      
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('revoked', 'Revoked'),
    ], string='Status', default='draft', required=True, tracking=True)
      
    usage_log_ids = fields.One2many(
        'ai_token_tracker.usage_log', 
        'api_key_id', 
        string='Usage Logs'
    )
      
    # --- Encryption Helper Methods ---
      
    def _get_encryption_key(self):
        """Fetches or creates a master encryption key from Odoo config."""
        config_param = self.env['ir.config_parameter'].sudo()
        master_key = config_param.get_param('ai_token_tracker.master_key')
        if not master_key:
            # Generate a new 32-byte (256-bit) key
            new_key = get_random_bytes(32)
            master_key_b64 = base64.b64encode(new_key).decode('utf-8')
            config_param.set_param('ai_token_tracker.master_key', master_key_b64)
            master_key = master_key_b64
          
        # Decode the base64 key for use in AES
        return base64.b64decode(master_key)

    def _encrypt(self, plaintext):
        """Encrypts plaintext using AES-256-CBC."""
        key = self._get_encryption_key()
        # Generate a random 16-byte IV
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # Pad the plaintext to be a multiple of the block size
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        # Prepend the IV to the ciphertext for storage
        return base64.b64encode(iv + ciphertext).decode('utf-8')

    def _decrypt(self, b64_ciphertext):
        """Decrypts AES-256-CBC ciphertext."""
        key = self._get_encryption_key()
        try:
            # Decode from base64
            encrypted_data = base64.b64decode(b64_ciphertext)
            # Extract the IV (first 16 bytes)
            iv = encrypted_data[:AES.block_size]
            ciphertext = encrypted_data[AES.block_size:]
            # Create cipher object and decrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(ciphertext)
            # Unpad the decrypted data
            return unpad(decrypted_padded, AES.block_size).decode('utf-8')
        except Exception as e:
            # Log the error, but return a generic message
            return "Error decrypting key."

    # --- ORM Method Overrides for Encryption ---
      
    @api.model
    def create(self, vals):
        """Overrides create to encrypt the key_value."""
        if 'key_value' in vals and vals['key_value']:
            plaintext_key = vals['key_value']
            # Only encrypt if it's not already an encrypted marker
            if not plaintext_key.startswith('enc::'):
                vals['key_value'] = f"enc::{self._encrypt(plaintext_key)}"
        return super(AiApiKey, self).create(vals)

    def write(self, vals):
        """Overrides write to encrypt the key_value if it's being changed."""
        if 'key_value' in vals and vals['key_value']:
            plaintext_key = vals['key_value']
            # Handle user trying to re-save an existing key
            if plaintext_key.startswith('enc::'):
                vals.pop('key_value') # Don't re-encrypt
            elif plaintext_key == '**********':
                vals.pop('key_value') # Don't save the mask
            else:
                vals['key_value'] = f"enc::{self._encrypt(plaintext_key)}"
        return super(AiApiKey, self).write(vals)

    def read(self, fields=None, load='_classic_read'):
        """
        Overrides read to decrypt the key_value ONLY for managers.
        Other users will see a mask.
        """
        is_manager = self.env.user.has_group('ai_token_tracker.group_ai_token_tracker_manager')
          
        # Perform the actual read
        results = super(AiApiKey, self).read(fields=fields, load=load)
          
        # Check if key_value was requested and we are processing results
        if fields and 'key_value' in fields and results:
            for res in results:
                if 'key_value' in res and res['key_value'] and res['key_value'].startswith('enc::'):
                    encrypted_val = res['key_value'][5:] # Strip 'enc::'
                    if is_manager:
                        # Decrypt only for managers
                        res['key_value'] = self._decrypt(encrypted_val)
                    else:
                        # Show mask for everyone else
                        res['key_value'] = '**********'
        return results

    def action_activate(self):
        self.write({'state': 'active'})

    def action_revoke(self):
        self.write({'state': 'revoked'})