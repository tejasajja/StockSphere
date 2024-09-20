
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils'; 
import { ModeToggle } from '../mode-toggle';

// eslint-disable-next-line react/prop-types
export function MainNav({ className, ...props }) {
  return (
    <nav className={cn('flex items-center space-x-4 lg:space-x-6', className)} {...props}>
      <ModeToggle/>
      <NavLink 
        to="/stockdashboard" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Stocks
      </NavLink>
      <NavLink 
        to="/stockanalysis" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Stock Analysis
      </NavLink>
      <NavLink 
        to="/cryptodashboard" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Crypto
      </NavLink>
      <NavLink 
        to="/cryptoanalysis" 
        className={({ isActive }) => isActive ? "text-sm font-medium transition-colors text-primary" : "text-sm font-medium transition-colors text-muted-foreground"}
      >
        Crypto Analysis
      </NavLink>
    </nav>
  );
}

export default MainNav;
