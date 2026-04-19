import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Cog, Save, User, Palette, Database, Bell, Target, Download, Trash2, Moon, Sun, Monitor } from 'lucide-react';
import { useState, useEffect } from 'react';
import { authApi } from '../api/auth';

const SettingsPage = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('light');
  const [emissionTarget, setEmissionTarget] = useState('1000');
  const [notifications, setNotifications] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(false);
  const [userData, setUserData] = useState({
    email: '',
    full_name: '',
    institution_name: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'auto' || 'light';
    setTheme(savedTheme);

    // Fetch current user data
    const fetchUserData = async () => {
      try {
        const response = await authApi.getCurrentUser();
        setUserData({
          email: response.data.email,
          full_name: response.data.full_name || '',
          institution_name: response.data.institution_name || '',
        });
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'auto') => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);

    if (newTheme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', prefersDark);
    } else {
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 fade-in">
        <div className="p-3 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-xl shadow-lg">
          <Cog className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold gradient-text">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Customize your CarbonTrace experience</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Appearance */}
        <Card className="glass-card border-0 shadow-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-3">Theme</Label>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  className={`flex flex-col gap-1 h-auto py-3 ${theme === 'light' ? 'bg-gradient-to-r from-carbon-emerald to-carbon-leaf' : ''}`}
                  onClick={() => handleThemeChange('light')}
                >
                  <Sun className="h-4 w-4" />
                  <span className="text-xs">Light</span>
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  className={`flex flex-col gap-1 h-auto py-3 ${theme === 'dark' ? 'bg-gradient-to-r from-carbon-emerald to-carbon-leaf' : ''}`}
                  onClick={() => handleThemeChange('dark')}
                >
                  <Moon className="h-4 w-4" />
                  <span className="text-xs">Dark</span>
                </Button>
                <Button
                  variant={theme === 'auto' ? 'default' : 'outline'}
                  className={`flex flex-col gap-1 h-auto py-3 ${theme === 'auto' ? 'bg-gradient-to-r from-carbon-emerald to-carbon-leaf' : ''}`}
                  onClick={() => handleThemeChange('auto')}
                >
                  <Monitor className="h-4 w-4" />
                  <span className="text-xs">Auto</span>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Emission Targets */}
        <Card className="glass-card border-0 shadow-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Emission Targets
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="target" className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Annual CO2 Target (tons)</Label>
              <Input
                id="target"
                type="number"
                value={emissionTarget}
                onChange={(e) => setEmissionTarget(e.target.value)}
                className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Set your annual carbon emission reduction goal</p>
            </div>
            <Button className="w-full glow-green">
              <Target className="h-4 w-4 mr-2" />
              Save Target
            </Button>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="glass-card border-0 shadow-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">Push Notifications</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Get alerts for important updates</p>
              </div>
              <button
                onClick={() => setNotifications(!notifications)}
                className={`w-12 h-6 rounded-full transition-colors ${notifications ? 'bg-carbon-emerald' : 'bg-gray-300 dark:bg-gray-600'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full transition-transform ${notifications ? 'translate-x-6' : 'translate-x-0.5'}`} />
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">Email Alerts</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">Receive emission reports via email</p>
              </div>
              <button
                onClick={() => setEmailAlerts(!emailAlerts)}
                className={`w-12 h-6 rounded-full transition-colors ${emailAlerts ? 'bg-carbon-emerald' : 'bg-gray-300 dark:bg-gray-600'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full transition-transform ${emailAlerts ? 'translate-x-6' : 'translate-x-0.5'}`} />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Data Management */}
        <Card className="glass-card border-0 shadow-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Data Management
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start border-gray-200 dark:border-gray-600 hover:bg-carbon-emerald/10">
              <Download className="h-4 w-4 mr-2" />
              Export All Data
            </Button>
            <Button variant="outline" className="w-full justify-start border-gray-200 dark:border-gray-600 hover:bg-carbon-emerald/10">
              <Database className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
            <Button variant="outline" className="w-full justify-start border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 hover:text-red-700">
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All Data
            </Button>
          </CardContent>
        </Card>

        {/* Profile */}
        <Card className="glass-card border-0 shadow-2xl lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Profile Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="fullName" className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Full Name</Label>
                <Input
                  id="fullName"
                  value={loading ? 'Loading...' : userData.full_name}
                  onChange={(e) => setUserData({ ...userData, full_name: e.target.value })}
                  className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
                />
              </div>
              <div>
                <Label htmlFor="email" className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={loading ? 'Loading...' : userData.email}
                  disabled
                  className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800 opacity-75"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="institution" className="text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">Institution Name</Label>
              <Input
                id="institution"
                value={loading ? 'Loading...' : userData.institution_name}
                onChange={(e) => setUserData({ ...userData, institution_name: e.target.value })}
                className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
              />
            </div>
            <Button className="glow-green">
              <Save className="h-4 w-4 mr-2" />
              Save Profile
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SettingsPage;

