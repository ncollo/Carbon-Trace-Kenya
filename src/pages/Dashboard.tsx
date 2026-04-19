import { useState, useEffect } from 'react';
import { emissionsApi } from '../api/emissions';
import { DashboardStats } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Car, Fuel, Leaf, Zap, Globe, ArrowUp, ArrowDown, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';


const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await emissionsApi.getDashboardStats();
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
        // Mock data for demo
        setStats({
          total_vehicles: 45,
          total_emissions: 1250.5,
          fuel_consumed: 8500.2,
          distance_traveled: 125000,
          emission_trend: [
            { month: 'Jan', emissions: 180 },
            { month: 'Feb', emissions: 195 },
            { month: 'Mar', emissions: 210 },
            { month: 'Apr', emissions: 185 },
            { month: 'May', emissions: 200 },
            { month: 'Jun', emissions: 280 },
          ],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-48 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-96"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-32 bg-gray-200 rounded-xl"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Vehicles',
      value: stats?.total_vehicles || 0,
      icon: Car,
      color: 'from-carbon-emerald to-carbon-leaf',
      bgColor: 'bg-gradient-to-br from-emerald-50 to-green-100',
      glow: 'shadow-glow-green',
      change: '+12%',
      changePositive: true,
    },
    {
      title: 'Total Emissions (tCO2e)',
      value: stats?.total_emissions?.toFixed(2) || '0',
      icon: Leaf,
      color: 'from-carbon-green to-carbon-emerald',
      bgColor: 'bg-gradient-to-br from-green-50 to-emerald-100',
      glow: 'shadow-glow-emerald',
      change: '-8%',
      changePositive: true,
    },
    {
      title: 'Fuel Consumed (L)',
      value: stats?.fuel_consumed?.toFixed(2) || '0',
      icon: Fuel,
      color: 'from-orange-500 to-amber-600',
      bgColor: 'bg-gradient-to-br from-orange-50 to-amber-100',
      glow: 'shadow-lg',
      change: '+5%',
      changePositive: false,
    },
    {
      title: 'Distance Traveled (km)',
      value: stats?.distance_traveled?.toLocaleString() || '0',
      icon: Activity,
      color: 'from-carbon-leaf to-carbon-emerald',
      bgColor: 'bg-gradient-to-br from-teal-50 to-emerald-100',
      glow: 'shadow-carbon-glow',
      change: '+15%',
      changePositive: true,
    },
  ];

  const pieData = [
    { name: 'Scope 1', value: 65, color: '#10b981' },
    { name: 'Scope 2', value: 25, color: '#059669' },
    { name: 'Scope 3', value: 10, color: '#047857' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Overview of your carbon emission data</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-700">
          <Leaf className="h-5 w-5 text-green-600 dark:text-green-400" />
          <span className="text-sm font-medium text-green-700 dark:text-green-300">Live Data</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className={`glass-card border-0 ${stat.glow} hover:scale-[1.03] transition-all duration-300 animate-fade-in`}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-200">
                  {stat.title}
                </CardTitle>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg animate-float`}>
                  <Icon className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                <div className={`flex items-center gap-1 mt-2 text-sm ${
                  stat.changePositive ? 'text-carbon-emerald dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
                }`}>
                  {stat.changePositive ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                  <span className="font-medium">{stat.change}</span>
                  <span className="text-gray-500 dark:text-gray-400">vs last month</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <Card className="lg:col-span-2 glass-card border-0 shadow-carbon-glow">
          <CardHeader>
            <CardTitle className="text-xl font-bold gradient-text">Emission Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300} minHeight={250}>
              <LineChart data={stats?.emission_trend || []}>
                <defs>
                  <linearGradient id="colorEmission" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                <XAxis dataKey="month" stroke="#6b7280" className="dark:stroke-gray-400" />
                <YAxis stroke="#6b7280" className="dark:stroke-gray-400" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                    backdropFilter: 'blur(10px)',
                    border: '1px solid hsl(var(--carbon-emerald) / 0.3)', 
                    borderRadius: '12px',
                    boxShadow: '0 10px 40px rgba(16, 185, 129, 0.2)'
                  }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="emissions" 
                  stroke="#10b981" 
                  strokeWidth={4}
                  fillOpacity={1}
                  fill="url(#colorEmission)"
                  dot={{ fill: '#10b981', strokeWidth: 3, r: 6 }}
                  activeDot={{ r: 8, stroke: '#10b981', strokeWidth: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass-card border-0 shadow-glow-green">
          <CardHeader>
            <CardTitle className="text-xl font-bold gradient-text">Emission Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300} minHeight={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.9)', 
                    backdropFilter: 'blur(10px)',
                    border: '1px solid hsl(var(--carbon-emerald) / 0.3)', 
                    borderRadius: '12px',
                    boxShadow: '0 10px 40px rgba(16, 185, 129, 0.2)'
                  }} 
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={36}
                  iconType="circle"
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card border-0 shadow-carbon-glow bg-gradient-to-br from-emerald-50/50 to-green-100/50">
        <CardHeader>
          <CardTitle className="text-xl font-bold gradient-text">Quick Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-lg shadow-lg animate-float">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Efficiency Gain</p>
                <p className="text-2xl font-bold text-carbon-emerald">+15%</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-green to-carbon-emerald rounded-lg shadow-lg animate-float" style={{ animationDelay: '0.2s' }}>
                <Globe className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Carbon Offset</p>
                <p className="text-2xl font-bold text-carbon-green">2,340 t</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-leaf to-carbon-emerald rounded-lg shadow-lg animate-float" style={{ animationDelay: '0.4s' }}>
                <Activity className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Active Projects</p>
                <p className="text-2xl font-bold text-carbon-leaf">8</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
