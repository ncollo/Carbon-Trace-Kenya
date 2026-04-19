export interface Vehicle {
  id: string;
  registration_number: string;
  vehicle_type: string;
  fuel_type: string;
  year: number;
  mileage: number;
}

export interface FuelRecord {
  id: string;
  vehicle_id: string;
  fuel_type: string;
  liters: number;
  cost: number;
  date: string;
  station: string;
}

export interface TravelReceipt {
  id: string;
  vehicle_id: string;
  distance_km: number;
  date: string;
  purpose: string;
  from_location: string;
  to_location: string;
}

export interface EmissionReport {
  id: string;
  institution_id: string;
  period: string;
  total_emissions: number;
  scope1_emissions: number;
  scope2_emissions: number;
  scope3_emissions: number;
  created_at: string;
}

export interface DashboardStats {
  total_vehicles: number;
  total_emissions: number;
  fuel_consumed: number;
  distance_traveled: number;
  emission_trend: Array<{
    month: string;
    emissions: number;
  }>;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  institution_name?: string;
  created_at: string;
}
