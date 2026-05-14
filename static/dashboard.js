/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AiMonitorDashboard extends Component {
    static template = "AI_token_tracker.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            stats: {
                total_subscriptions: 0,
                active_subscriptions: 0,
                total_cost_this_month: 0,
                total_usage_this_month: 0,
                total_energy_kwh: 0,
                total_co2_kg: 0,
                over_budget_count: 0,
            },
            top_models: [],
            recent_usage: [],
            subscriptions: [],
            currency_symbol: '$',
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Load statistics
            const subscriptions = await this.orm.searchRead(
                "ai_monitor.subscription",
                [],
                ["name", "state", "current_month_cost", "current_month_usage", 
                 "total_energy_kwh", "total_co2_kg", "monthly_budget", "budget_consumption_pct"]
            );

            // Calculate stats
            this.state.stats.total_subscriptions = subscriptions.length;
            this.state.stats.active_subscriptions = subscriptions.filter(s => s.state === 'active').length;
            this.state.stats.total_cost_this_month = subscriptions.reduce((sum, s) => sum + s.current_month_cost, 0);
            this.state.stats.total_usage_this_month = subscriptions.reduce((sum, s) => sum + s.current_month_usage, 0);
            this.state.stats.total_energy_kwh = subscriptions.reduce((sum, s) => sum + s.total_energy_kwh, 0);
            this.state.stats.total_co2_kg = subscriptions.reduce((sum, s) => sum + s.total_co2_kg, 0);
            this.state.stats.over_budget_count = subscriptions.filter(s => s.budget_consumption_pct >= 100).length;
            
            this.state.subscriptions = subscriptions.slice(0, 5);

            // Load top models by usage
            const usageLogs = await this.orm.searchRead(
                "ai_monitor.usage_log",
                [],
                ["model_id", "cost", "total_tokens"],
                { limit: 1000 }
            );

            // Aggregate by model
            const modelUsage = {};
            usageLogs.forEach(log => {
                const modelId = log.model_id[0];
                const modelName = log.model_id[1];
                if (!modelUsage[modelId]) {
                    modelUsage[modelId] = { name: modelName, count: 0, cost: 0, tokens: 0 };
                }
                modelUsage[modelId].count += 1;
                modelUsage[modelId].cost += log.cost;
                modelUsage[modelId].tokens += log.total_tokens;
            });

            this.state.top_models = Object.values(modelUsage)
                .sort((a, b) => b.count - a.count)
                .slice(0, 5);

            // Load recent usage
            this.state.recent_usage = await this.orm.searchRead(
                "ai_monitor.usage_log",
                [],
                ["timestamp", "model_id", "subscription_id", "cost", "total_tokens"],
                { limit: 10, order: "timestamp desc" }
            );

        } catch (error) {
            console.error("Error loading dashboard data:", error);
        }
    }

    formatCurrency(value) {
        return `${this.state.currency_symbol}${value.toFixed(2)}`;
    }

    formatNumber(value) {
        return value.toLocaleString();
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    openSubscriptions() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'ai_monitor.subscription',
            views: [[false, 'list'], [false, 'form']],
            view_mode: 'list,form',
        });
    }

    openUsageLogs() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'ai_monitor.usage_log',
            views: [[false, 'list'], [false, 'form']],
            view_mode: 'list,form',
        });
    }

    openModels() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'ai_monitor.model',
            views: [[false, 'list'], [false, 'form']],
            view_mode: 'list,form',
        });
    }
}

registry.category("actions").add("ai_monitor.dashboard", AiMonitorDashboard);
