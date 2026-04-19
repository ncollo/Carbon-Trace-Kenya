import { Link, useLocation } from 'react-router-dom';
import { Leaf, BarChart3, Car, FileText, LogOut, User, Settings, Bell, ChevronDown } from 'lucide-react';
import { Button } from './ui/button';
import DarkToggle from './DarkToggle';
import { useState } from 'react';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const [showNotifs, setShowNotifs] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Vehicles', href: '/vehicles', icon: Car },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const notifications = [
    { id: 1, title: 'New emission report ready', time: '2 min ago', unread: true },
    { id: 2, title: 'Vehicle maintenance due', time: '1 day ago', unread: false },
    { id: 3, title: 'Carbon offset opportunity', time: '3 days ago', unread: false },
  ];

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen relative glass">
      {/* Top Navigation Bar */}
      <div className="bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 shadow-lg">
        <div className="px-4 lg:px-8 py-3">
          <div className="flex items-center justify-between gap-8">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center space-x-3 group flex-shrink-0">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl blur-lg opacity-20 group-hover:opacity-40 transition-opacity"></div>
                <div className="relative bg-gradient-to-br from-green-500 to-emerald-600 p-2 rounded-xl shadow-lg">
                  <Leaf className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="hidden sm:block">
                <span className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent">
                  CarbonTrace
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">by EmitIQ</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center space-x-1 flex-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 group ${
                      isActive
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-md shadow-green-500/30'
                        : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200'}`} />
                    <span className={`font-medium text-sm ${isActive ? 'text-white' : ''}`}>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Right side */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <DarkToggle />
              {/* Notifications Dropdown */}
              <div className="relative">
                <Button variant="ghost" size="icon" className="relative glow-green hover:bg-carbon-emerald/20 dark:hover:bg-gray-700" onClick={() => setShowNotifs(!showNotifs)}>
                  <Bell className="h-4 w-4 dark:text-gray-200" />
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-900" />
                </Button>
                {showNotifs && (
                  <div className="absolute top-full right-0 mt-2 w-80 bg-white dark:bg-gray-800 glass-card shadow-2xl border rounded-2xl z-50 animate-fade-in">
                    <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">Notifications</h3>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                      {notifications.map((notif) => (
                        <div key={notif.id} className="p-4 border-b border-gray-50 dark:border-gray-800 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 dark:text-gray-100">{notif.title}</p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">{notif.time}</p>
                            </div>
                            {notif.unread && (
                              <div className="ml-2">
                                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {/* Profile Dropdown */}
              <div className="relative">
                <Button variant="ghost" size="icon" className="glow-green hover:bg-carbon-emerald/20 dark:hover:bg-gray-700" onClick={() => setShowProfile(!showProfile)}>
                  <div className="w-9 h-9 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-full flex items-center justify-center shadow-lg">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <ChevronDown className="h-3.5 w-3.5 ml-1 transition-transform duration-200 dark:text-gray-200" style={{ transform: showProfile ? 'rotate(180deg)' : 'rotate(0deg)' }} />
                </Button>
                {showProfile && (
                  <div className="absolute top-full right-0 mt-2 w-56 bg-white dark:bg-gray-800 glass-card shadow-2xl border rounded-2xl z-50 animate-fade-in">
                    <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">Admin</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">admin@emitiq.com</p>
                      </div>
                    </div>
                    <div className="py-2">
                      <Link to="/settings" className="flex items-center px-4 py-3 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors w-full">
                        <Settings className="h-4 w-4 mr-3 dark:text-gray-400" />
                        Settings
                      </Link>
                      <Button variant="ghost" className="justify-start w-full text-sm text-gray-700 dark:text-gray-200 hover:bg-red-50 dark:hover:bg-red-900/20 h-auto py-3 px-4" onClick={handleLogout}>
                        <LogOut className="h-4 w-4 mr-3" />
                        Logout
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Page content */}
      <div className="min-h-screen overflow-auto">
        {children}
      </div>
    </div>
  );
};

export default Layout;
