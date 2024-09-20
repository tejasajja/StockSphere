import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils'; 
import { ModeToggle } from '../mode-toggle';

export function AdminMainNav({ className, ...props }) {
  
  return (
    <nav className={cn('flex items-center space-x-4 lg:space-x-6', className)} {...props}>
      <ModeToggle/>
      <NavLink 
        to="/admin/transactions" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Transactions
      </NavLink>
      <NavLink 
        to="/admin/customers" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Customers
      </NavLink>
      <NavLink 
        to="/admin/stocks" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Stock Data
      </NavLink>
      <NavLink 
        to="/admin/crypto" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Crypto Data
      </NavLink>
      <NavLink 
        to="/admin/agent" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Agent Data
      </NavLink>
      <h1 className='pl-32 text-2xl font-bold'>Admin Dashboard</h1>
    </nav>
  );
}

export default AdminMainNav;
