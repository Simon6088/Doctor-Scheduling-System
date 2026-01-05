<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>工作量统计</span>
        <div class="filters">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              :clearable="false"
              style="width: 250px"
            />
            <el-select v-model="selectedDept" placeholder="选择科室" clearable style="width: 150px">
               <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id"/>
            </el-select>
            <el-button type="primary" @click="fetchStats">查询</el-button>
            <el-button type="success" @click="exportToCSV">导出报表</el-button>
        </div>
      </div>
    </template>
    
    <div class="charts-row" v-if="stats.length > 0">
        <div class="chart-wrapper">
            <v-chart class="chart" :option="barOption" autoresize />
        </div>
        <div class="chart-wrapper">
             <v-chart class="chart" :option="pieOption" autoresize />
        </div>
    </div>
    
    <el-table :data="stats" stripe style="width: 100%; margin-top: 20px;">
       <el-table-column prop="doctor_name" label="医生" />
       <el-table-column prop="total_shifts" label="总班次" sortable />
       <el-table-column prop="night_shifts" label="夜班数" sortable />
       <el-table-column prop="weekend_shifts" label="周末班次" sortable />
       <el-table-column prop="holiday_shifts" label="节假日班数" sortable />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components';
import api from '../api/axios';
import { ElMessage } from 'element-plus';

use([CanvasRenderer, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent]);

const dateRange = ref([]);
const selectedDept = ref('');
const departments = ref([]);
const stats = ref([]);

const initDates = () => {
    const start = new Date();
    start.setDate(1);
    const end = new Date();
    end.setMonth(end.getMonth() + 1);
    end.setDate(0);
    
    const fmt = (d) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    };
    
    dateRange.value = [fmt(start), fmt(end)];
};

const fetchDepartments = async () => {
    try {
        const res = await api.get('/departments/');
        departments.value = res.data;
    } catch { }
};

const fetchStats = async () => {
    if (!dateRange.value || dateRange.value.length < 2) return;
    
    const params = {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1]
    };
    if (selectedDept.value) {
        params.department_id = selectedDept.value;
    }
    
    try {
        const res = await api.get('/stats/workload', { params });
        stats.value = res.data;
        ElMessage.success('查询成功');
    } catch(e) {
        console.error(e);
        ElMessage.error('查询失败');
    }
};

const exportToCSV = () => {
    if (stats.value.length === 0) {
        ElMessage.warning('无数据可导出');
        return;
    }
    
    const headers = ['医生ID', '医生姓名', '总班次', '夜班', '周末班', '节假日班'];
    const rows = stats.value.map(s => [
        s.doctor_id,
        s.doctor_name,
        s.total_shifts,
        s.night_shifts,
        s.weekend_shifts,
        s.holiday_shifts
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `workload_stats_${dateRange.value[0]}_${dateRange.value[1]}.csv`;
    link.click();
};

const barOption = computed(() => {
    const names = stats.value.map(s => s.doctor_name);
    const totals = stats.value.map(s => s.total_shifts);
    const nights = stats.value.map(s => s.night_shifts);
    
    return {
        title: { text: '工作量明细' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['总班次', '夜班'] },
        xAxis: { type: 'category', data: names, axisLabel: { interval: 0, rotate: 30 } },
        yAxis: { type: 'value' },
        series: [
            { name: '总班次', type: 'bar', data: totals, itemStyle: { color: '#409EFF' } },
            { name: '夜班', type: 'bar', data: nights, itemStyle: { color: '#E6A23C' } }
        ],
        grid: { bottom: 60 }
    };
});

const pieOption = computed(() => {
    const data = stats.value.map(s => ({
        name: s.doctor_name,
        value: s.total_shifts
    }));
    return {
        title: { text: '总班次占比', left: 'center' },
        tooltip: { trigger: 'item' },
        series: [
             {
                 name: '总班次',
                 type: 'pie',
                 radius: '50%',
                 data: data,
                 emphasis: {
                     itemStyle: {
                         shadowBlur: 10,
                         shadowOffsetX: 0,
                         shadowColor: 'rgba(0, 0, 0, 0.5)'
                     }
                 }
             }
        ]
    };
});

onMounted(() => {
    initDates();
    fetchDepartments();
    fetchStats();
});
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.filters { display: flex; gap: 10px; align-items: center; }
.charts-row { display: flex; gap: 20px; height: 400px; margin-top: 20px; }
.chart-wrapper { flex: 1; height: 100%; border: 1px solid #eee; padding: 10px; border-radius: 4px; }
.chart { height: 100%; width: 100%; }
</style>
