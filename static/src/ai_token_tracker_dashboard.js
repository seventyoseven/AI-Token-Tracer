/** @odoo-module **/

import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { rpc } from "@web/core/network/rpc";

class AITokenTrackerDashboard extends Component {
    static template = "ai_token_tracker.Dashboard";

    setup() {
        this.action = useService("action");
          
        // State for KPIs
        this.state = useState({
            kpis: {
                total_cost_usd: "0.00",
                total_energy_kwh: "0.000",
                total_co2_kg: "0.00",
                total_savings_kwh: "0.000",
                total_savings_usd: "0.00",
            },
            date_filter: "this_month",
        });

        // Refs for Chart canvases
        this.energyChartRef = useRef("energyByModelChart");
        this.costChartRef = useRef("costByPurposeChart");

        // Chart.js objects
        this.energyChart = null;
        this.costChart = null;

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.fetchDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async fetchDashboardData() {
        // Fetch KPI data
        const kpiData = await rpc("/ai_token_tracker/get_kpis", {
            date_filter: this.state.date_filter,
        });
        this.state.kpis = kpiData;

        // Fetch Chart data
        const chartData = await rpc("/ai_token_tracker/get_chart_data", {
            date_filter: this.state.date_filter,
        });
          
        this.chartData = chartData; // Store for rendering
    }

    renderCharts() {
        // Render Energy by Model Chart (Bar)
        if (this.energyChart) {
            this.energyChart.destroy();
        }
        if (this.energyChartRef.el) {
            this.energyChart = new Chart(this.energyChartRef.el, {
                type: 'bar',
                data: this.chartData.energy_by_model,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { 
                            display: true, 
                            text: 'Energy Consumed by Model (kWh)',
                            font: { size: 12 }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { font: { size: 9 } }
                        },
                        y: {
                            ticks: { font: { size: 9 } }
                        }
                    }
                }
            });
        }

        // Render Cost by Purpose Chart (Pie)
        if (this.costChart) {
            this.costChart.destroy();
        }
        if (this.costChartRef.el) {
            this.costChart = new Chart(this.costChartRef.el, {
                type: 'pie',
                data: this.chartData.cost_by_purpose,
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1.3,
                    plugins: {
                        legend: { 
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                padding: 8,
                                font: { size: 9 }
                            }
                        },
                        title: { 
                            display: true, 
                            text: 'Cost by Purpose (USD)',
                            font: { size: 12 }
                        }
                    },
                    layout: {
                        padding: { left: 5, right: 5, top: 5, bottom: 5 }
                    }
                }
            });
        }
    }

    async onDateFilterChange(ev) {
        this.state.date_filter = ev.target.value;
        await this.fetchDashboardData();
        this.renderCharts(); // Re-render charts with new data
    }
    
    // Action methods to open views
    openOptimizations() {
        this.action.doAction("AI_token_tracker.action_ai_suggestion");
    }
    
    openLogs() {
        this.action.doAction("AI_token_tracker.action_ai_usage_log");
    }
}

// Register the component as a client action
registry.category("actions").add("ai_token_tracker.dashboard", AITokenTrackerDashboard);