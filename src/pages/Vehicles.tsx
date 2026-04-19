import { useState, useEffect } from 'react';
import { emissionsApi } from '../api/emissions';
import { Vehicle } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Plus, Car, Fuel, Calendar, Search, Filter, CheckCircle, XCircle, Clock, MoreVertical, Edit, Trash2, Leaf } from 'lucide-react';

const Vehicles = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [newVehicle, setNewVehicle] = useState({
    registration_number: '',
    vehicle_type: '',
    fuel_type: '',
    year: new Date().getFullYear(),
    mileage: 0,
  });

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const response = await emissionsApi.getVehicles();
        setVehicles(response.data);
      } catch (error) {
        console.error('Failed to fetch vehicles:', error);
        // Mock data for demo
        setVehicles([
          { id: '1', registration_number: 'KAA 123A', vehicle_type: 'Sedan', fuel_type: 'Petrol', year: 2020, mileage: 45000 },
          { id: '2', registration_number: 'KCB 456B', vehicle_type: 'SUV', fuel_type: 'Diesel', year: 2021, mileage: 32000 },
          { id: '3', registration_number: 'KCC 789C', vehicle_type: 'Van', fuel_type: 'Diesel', year: 2019, mileage: 68000 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchVehicles();
  }, []);

  const handleAddVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await emissionsApi.createVehicle(newVehicle);
      setVehicles([...vehicles, response.data]);
      setShowAddForm(false);
      setNewVehicle({
        registration_number: '',
        vehicle_type: '',
        fuel_type: '',
        year: new Date().getFullYear(),
        mileage: 0,
      });
    } catch (error) {
      console.error('Failed to add vehicle:', error);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-64"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-48 bg-gray-200 rounded-xl"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const filteredVehicles = vehicles.filter((vehicle) => {
    const matchesSearch = vehicle.registration_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          vehicle.vehicle_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || vehicle.fuel_type.toLowerCase() === filterType.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  const fuelTypes = ['all', ...Array.from(new Set(vehicles.map(v => v.fuel_type)))];

  const getVehicleStatus = (year: number) => {
    const currentYear = new Date().getFullYear();
    if (currentYear - year < 3) return { status: 'New', color: 'bg-emerald-100 text-carbon-emerald border-emerald-200', icon: CheckCircle, glow: 'shadow-glow-green' };
    if (currentYear - year < 7) return { status: 'Good', color: 'bg-green-100 text-carbon-green border-green-200', icon: Clock, glow: 'shadow-carbon-glow' };
    return { status: 'Old', color: 'bg-teal-100 text-carbon-leaf border-teal-200', icon: XCircle, glow: 'shadow-lg' };
  };

  const calculateEmissions = (vehicle: Vehicle) => {
    // CO2 emissions in kg per km based on fuel type
    const emissionFactors: { [key: string]: number } = {
      'Petrol': 0.21,      // Modern unleaded petrol
      'Diesel': 0.24,      // Diesel fuel
      'Electric': 0.05,    // Electric (grid emissions)
      'Hybrid': 0.12,      // Hybrid (petrol + electric)
    };

    const factor = emissionFactors[vehicle.fuel_type] || 0.21;
    const annualEmissions = vehicle.mileage * factor;
    const co2Tons = annualEmissions / 1000;

    return {
      annualEmissions: annualEmissions.toFixed(2),
      co2Tons: co2Tons.toFixed(3),
      efficiency: factor <= 0.12 ? 'Eco-Friendly' : factor <= 0.22 ? 'Moderate' : 'High Emission',
      efficiencyColor: factor <= 0.12 ? 'text-green-600' : factor <= 0.22 ? 'text-yellow-600' : 'text-red-600',
    };
  };

  const totalEmissions = vehicles.reduce((sum, v) => sum + parseFloat(calculateEmissions(v).co2Tons), 0);
  const ecoVehicles = vehicles.filter(v => calculateEmissions(v).efficiency === 'Eco-Friendly').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">
            Vehicles
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your fleet vehicles</p>
        </div>
        <Button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-gradient-to-r from-carbon-emerald to-carbon-leaf hover:from-carbon-green hover:to-carbon-emerald shadow-glow-green animate-glow"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Vehicle
        </Button>
      </div>

      {/* Fleet Statistics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="glass-card bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20 rounded-2xl p-6 border-0 shadow-lg hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-between mb-2">
            <Car className="h-6 w-6 text-carbon-emerald" />
            <span className="text-xs font-semibold text-green-600 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">Total Fleet</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{vehicles.length}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Vehicles</p>
        </div>

        <div className="glass-card bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl p-6 border-0 shadow-lg hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-between mb-2">
            <Leaf className="h-6 w-6 text-blue-600" />
            <span className="text-xs font-semibold text-blue-600 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">CO2 Emissions</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{totalEmissions.toFixed(2)}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Tons CO2</p>
        </div>

        <div className="glass-card bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 rounded-2xl p-6 border-0 shadow-lg hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-between mb-2">
            <Leaf className="h-6 w-6 text-green-600" />
            <span className="text-xs font-semibold text-green-600 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">Eco-Friendly</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{ecoVehicles}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Vehicles</p>
        </div>

        <div className="glass-card bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl p-6 border-0 shadow-lg hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-between mb-2">
            <Fuel className="h-6 w-6 text-purple-600" />
            <span className="text-xs font-semibold text-purple-600 bg-purple-100 dark:bg-purple-900/30 px-2 py-1 rounded-full">Avg Mileage</span>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            {vehicles.length > 0 ? Math.round(vehicles.reduce((sum, v) => sum + v.mileage, 0) / vehicles.length).toLocaleString() : 0}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">km</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-carbon-emerald dark:text-emerald-400" />
          <Input
            placeholder="Search vehicles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-carbon-emerald dark:text-emerald-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="h-11 px-4 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass"
          >
            {fuelTypes.map((type) => (
              <option key={type} value={type} className="capitalize">
                {type === 'all' ? 'All Fuel Types' : type}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        <span className="font-medium">{filteredVehicles.length}</span>
        <span>vehicles found</span>
      </div>

      {showAddForm && (
        <Card className="glass-card border-0 shadow-glow-green bg-gradient-to-br from-emerald-50/50 dark:from-emerald-900/20 dark:to-green-900/20 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-xl font-bold gradient-text">Add New Vehicle</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddVehicle} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="registration" className="text-gray-700 dark:text-gray-200 font-medium">Registration Number</Label>
                  <Input
                    id="registration"
                    value={newVehicle.registration_number}
                    onChange={(e) => setNewVehicle({ ...newVehicle, registration_number: e.target.value })}
                    required
                    className="h-11 border-gray-200 focus:border-carbon-emerald focus:ring-carbon-emerald/20 glass"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="type" className="text-gray-700 dark:text-gray-200 font-medium">Vehicle Type</Label>
                  <Input
                    id="type"
                    value={newVehicle.vehicle_type}
                    onChange={(e) => setNewVehicle({ ...newVehicle, vehicle_type: e.target.value })}
                    required
                    className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fuel" className="text-gray-700 dark:text-gray-200 font-medium">Fuel Type</Label>
                  <select
                    id="fuel"
                    value={newVehicle.fuel_type}
                    onChange={(e) => setNewVehicle({ ...newVehicle, fuel_type: e.target.value })}
                    required
                    className="h-11 w-full px-4 rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass"
                  >
                    <option value="">Select fuel type</option>
                    <option value="Petrol">Petrol (Unleaded)</option>
                    <option value="Diesel">Diesel</option>
                    <option value="Electric">Electric</option>
                    <option value="Hybrid">Hybrid</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="year" className="text-gray-700 dark:text-gray-200 font-medium">Year</Label>
                  <Input
                    id="year"
                    type="number"
                    value={newVehicle.year}
                    onChange={(e) => setNewVehicle({ ...newVehicle, year: parseInt(e.target.value) })}
                    required
                    className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="mileage" className="text-gray-700 dark:text-gray-200 font-medium">Mileage (km)</Label>
                  <Input
                    id="mileage"
                    type="number"
                    value={newVehicle.mileage}
                    onChange={(e) => setNewVehicle({ ...newVehicle, mileage: parseInt(e.target.value) })}
                    required
                    className="h-11 border-gray-200 dark:border-gray-600 focus:border-carbon-emerald dark:focus:border-emerald-500 focus:ring-carbon-emerald/20 glass bg-white dark:bg-gray-800"
                  />
                </div>
              </div>
              <div className="flex gap-3">
                <Button 
                  type="submit"
                  className="bg-gradient-to-r from-carbon-emerald to-carbon-leaf hover:from-carbon-green hover:to-carbon-emerald shadow-glow-green"
                >
                  Add Vehicle
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowAddForm(false)}
                  className="border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {filteredVehicles.map((vehicle) => {
          const vehicleStatus = getVehicleStatus(vehicle.year);
          const StatusIcon = vehicleStatus.icon;
          return (
            <Card 
              key={vehicle.id} 
              className={`glass-card border-0 hover:scale-[1.03] transition-all duration-300 group ${vehicleStatus.glow}`}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-lg shadow-lg animate-float">
                      <Car className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg font-bold gradient-text">
                        {vehicle.registration_number}
                      </CardTitle>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${vehicleStatus.color}`}>
                        <StatusIcon className="h-3 w-3" />
                        {vehicleStatus.status}
                      </span>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-carbon-emerald/20 dark:hover:bg-emerald-900/30">
                    <MoreVertical className="h-4 w-4 text-carbon-emerald dark:text-emerald-400" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Fuel className="h-4 w-4 text-carbon-emerald dark:text-emerald-400" />
                      <span className="font-medium">Fuel:</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded border border-emerald-200 dark:border-emerald-700">
                      {vehicle.fuel_type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <Calendar className="h-4 w-4 text-carbon-emerald dark:text-emerald-400" />
                      <span className="font-medium">Year:</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded border border-emerald-200 dark:border-emerald-700">
                      {vehicle.year}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Type:</span>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded border border-emerald-200 dark:border-emerald-700">
                      {vehicle.vehicle_type}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Mileage:</span>
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded border border-emerald-200 dark:border-emerald-700">
                      {vehicle.mileage.toLocaleString()} km
                    </span>
                  </div>
                </div>
                <div className="pt-3 border-t border-emerald-100 dark:border-emerald-800">
                  <div className="bg-gradient-to-r from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-1">
                        <Leaf className="h-3 w-3 text-green-600" />
                        CO2 Emissions
                      </span>
                      <span className={`text-xs font-bold ${calculateEmissions(vehicle).efficiencyColor}`}>
                        {calculateEmissions(vehicle).efficiency}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Annual:</span>
                      <span className="text-xs font-semibold text-gray-900 dark:text-gray-100">
                        {calculateEmissions(vehicle).annualEmissions} kg
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Total:</span>
                      <span className="text-xs font-semibold text-gray-900 dark:text-gray-100">
                        {calculateEmissions(vehicle).co2Tons} tons
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 pt-3 border-t border-emerald-100 dark:border-emerald-800">
                  <Button size="sm" variant="outline" className="flex-1 border-carbon-emerald/30 hover:bg-carbon-emerald/10 hover:border-carbon-emerald hover:text-carbon-emerald dark:hover:bg-emerald-900/20">
                    <Edit className="h-3 w-3 mr-1" />
                    Edit
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1 border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 hover:text-red-700">
                    <Trash2 className="h-3 w-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredVehicles.length === 0 && (
        <div className="text-center py-12 glass-card rounded-2xl">
          <div className="p-4 bg-gradient-to-br from-carbon-emerald to-carbon-leaf rounded-full w-16 h-16 mx-auto mb-4 shadow-glow-green animate-float">
            <Car className="h-8 w-8 text-white" />
          </div>
          <p className="text-gray-500 dark:text-gray-400 text-lg">No vehicles found</p>
          <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">Try adjusting your search or filter</p>
        </div>
      )}
    </div>
  );
};

export default Vehicles;
