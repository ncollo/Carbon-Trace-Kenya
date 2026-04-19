import { useState, useEffect } from 'react';
import { emissionsApi } from '../api/emissions';
import { EmissionReport } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FileText, Download, Calendar, FileDown, TrendingDown, CheckCircle, Clock, AlertCircle, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const Reports = () => {
  const [reports, setReports] = useState<EmissionReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await emissionsApi.getReports();
        setReports(response.data);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
        // Mock data for demo
        setReports([
          {
            id: '1',
            institution_id: 'INST001',
            period: '2024-Q1',
            total_emissions: 1250.5,
            scope1_emissions: 850.3,
            scope2_emissions: 280.2,
            scope3_emissions: 120.0,
            created_at: '2024-04-01T00:00:00Z',
          },
          {
            id: '2',
            institution_id: 'INST001',
            period: '2024-Q2',
            total_emissions: 1180.2,
            scope1_emissions: 790.1,
            scope2_emissions: 270.5,
            scope3_emissions: 119.6,
            created_at: '2024-07-01T00:00:00Z',
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const response = await emissionsApi.generateReport('2024-Q3');
      setReports([response.data, ...reports]);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (id: string) => {
    try {
      const response = await emissionsApi.downloadReport(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `emission-report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-40 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-80"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-64 bg-gray-200 rounded-xl"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getReportStatus = (report: EmissionReport) => {
    const daysSinceCreation = Math.floor((Date.now() - new Date(report.created_at).getTime()) / (1000 * 60 * 60 * 24));
    if (daysSinceCreation < 7) return { status: 'Recent', color: 'bg-emerald-100 text-carbon-emerald border-emerald-200', icon: CheckCircle, glow: 'shadow-glow-green' };
    if (daysSinceCreation < 30) return { status: 'This Month', color: 'bg-green-100 text-carbon-green border-green-200', icon: Clock, glow: 'shadow-carbon-glow' };
    return { status: 'Archived', color: 'bg-teal-100 text-carbon-leaf border-teal-200', icon: AlertCircle, glow: 'shadow-lg' };
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">
            Emission Reports
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">NSE-compliant carbon emission reports</p>
        </div>
        <Button 
          onClick={handleGenerateReport} 
          disabled={generating}
          className="bg-gradient-to-r from-carbon-emerald to-carbon-leaf hover:from-carbon-green hover:to-carbon-emerald shadow-glow-green animate-glow"
        >
          {generating ? (
            <span className="flex items-center gap-2">
              <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Generating...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <FileDown className="h-4 w-4" />
              Generate New Report
            </span>
          )}
        </Button>
      </div>

      <Card className="glass-card border-0 shadow-carbon-glow bg-gradient-to-br from-emerald-50/50 dark:from-emerald-900/20 dark:to-green-900/20">
        <CardHeader>
          <CardTitle className="text-xl font-bold gradient-text">Emission Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-lg shadow-lg animate-float">
                <TrendingDown className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Total Reduction</p>
                <p className="text-2xl font-bold text-carbon-emerald">-5.2%</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">vs last quarter</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-green to-carbon-emerald rounded-lg shadow-lg animate-float" style={{ animationDelay: '0.2s' }}>
                <FileText className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Reports Generated</p>
                <p className="text-2xl font-bold text-carbon-green">{reports.length}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">This year</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 glass rounded-xl shadow-sm hover:shadow-glow-green transition-all duration-300">
              <div className="p-3 bg-gradient-to-br from-carbon-leaf to-carbon-emerald rounded-lg shadow-lg animate-float" style={{ animationDelay: '0.4s' }}>
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Avg Emissions</p>
                <p className="text-2xl font-bold text-carbon-leaf">
                  {reports.length > 0 ? (reports.reduce((acc, r) => acc + r.total_emissions, 0) / reports.length).toFixed(0) : 0}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">tCO2e per report</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="lg:col-span-2 space-y-6">
          {reports.map((report) => {
            const reportStatus = getReportStatus(report);
            const StatusIcon = reportStatus.icon;
            const pieData = [
              { name: 'Scope 1', value: report.scope1_emissions, color: '#10b981' },
              { name: 'Scope 2', value: report.scope2_emissions, color: '#059669' },
              { name: 'Scope 3', value: report.scope3_emissions, color: '#047857' },
            ];
            return (
              <Card 
                key={report.id} 
                className={`glass-card border-0 hover:scale-[1.02] transition-all duration-300 ${reportStatus.glow}`}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-lg shadow-lg animate-float">
                        <FileText className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-bold gradient-text">
                          {report.period}
                        </CardTitle>
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${reportStatus.color}`}>
                          <StatusIcon className="h-3 w-3" />
                          {reportStatus.status}
                        </span>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleDownloadReport(report.id)}
                      className="bg-gradient-to-r from-carbon-emerald to-carbon-leaf hover:from-carbon-green hover:to-carbon-emerald shadow-glow-green"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download PDF
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
                    <div className="p-4 glass rounded-lg border border-emerald-200 dark:border-emerald-700 hover:shadow-glow-green transition-all duration-300">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Total Emissions</p>
                      <p className="text-2xl font-bold text-carbon-emerald">
                        {report.total_emissions.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">tCO2e</p>
                    </div>
                    <div className="p-4 glass rounded-lg border border-green-200 dark:border-green-700 hover:shadow-glow-green transition-all duration-300">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Scope 1</p>
                      <p className="text-xl font-bold text-carbon-green">
                        {report.scope1_emissions.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">tCO2e</p>
                    </div>
                    <div className="p-4 glass rounded-lg border border-teal-200 dark:border-teal-700 hover:shadow-glow-green transition-all duration-300">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Scope 2</p>
                      <p className="text-xl font-bold text-carbon-leaf">
                        {report.scope2_emissions.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">tCO2e</p>
                    </div>
                    <div className="p-4 glass rounded-lg border border-emerald-300 dark:border-emerald-700 hover:shadow-glow-green transition-all duration-300">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Scope 3</p>
                      <p className="text-xl font-bold text-emerald-700">
                        {report.scope3_emissions.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">tCO2e</p>
                    </div>
                  </div>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={70}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend verticalAlign="bottom" height={36} iconType="circle" />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-100 dark:border-gray-700">
                    <Calendar className="h-4 w-4 dark:text-emerald-400" />
                    <span>Created: {new Date(report.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card className="glass-card border-0 shadow-carbon-glow">
          <CardHeader>
            <CardTitle className="text-xl font-bold gradient-text">Emission Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350} minHeight={250}>
              <BarChart data={reports.map(r => ({
                period: r.period,
                total: r.total_emissions,
                scope1: r.scope1_emissions,
                scope2: r.scope2_emissions,
                scope3: r.scope3_emissions,
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                <XAxis dataKey="period" stroke="#6b7280" className="dark:stroke-gray-400" />
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
                <Legend />
                <Bar dataKey="total" fill="#10b981" name="Total" radius={[4, 4, 0, 0]} />
                <Bar dataKey="scope1" fill="#059669" name="Scope 1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="scope2" fill="#047857" name="Scope 2" radius={[4, 4, 0, 0]} />
                <Bar dataKey="scope3" fill="#065f46" name="Scope 3" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {reports.length === 0 && (
        <div className="text-center py-12 glass-card rounded-2xl">
          <div className="p-4 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-full w-16 h-16 mx-auto mb-4 shadow-glow-green animate-float">
            <FileText className="h-8 w-8 text-white" />
          </div>
          <p className="text-gray-500 dark:text-gray-400 text-lg">No reports found</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">Generate your first emission report</p>
        </div>
      )}
    </div>
  );
};

export default Reports;
