import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { BookOpen, User, LogOut, Settings, LayoutDashboard, Menu } from 'lucide-react';

export const Navbar = () => {
    const { user, logout, isAdmin } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-border">
            <div className="max-w-7xl mx-auto px-4 md:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 group" data-testid="nav-logo">
                        <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center group-hover:scale-105 transition-transform">
                            <BookOpen className="w-5 h-5 text-primary-foreground" />
                        </div>
                        <span className="font-heading text-xl font-semibold text-foreground">
                            CourseHub
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link 
                            to="/" 
                            className="text-muted-foreground hover:text-foreground transition-colors"
                            data-testid="nav-courses"
                        >
                            Browse Courses
                        </Link>
                        
                        {user ? (
                            <div className="flex items-center gap-4">
                                <Link to="/dashboard">
                                    <Button variant="ghost" className="gap-2" data-testid="nav-dashboard">
                                        <LayoutDashboard className="w-4 h-4" />
                                        Dashboard
                                    </Button>
                                </Link>
                                
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="outline" className="gap-2" data-testid="nav-user-menu">
                                            <User className="w-4 h-4" />
                                            {user.name}
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end" className="w-48">
                                        <DropdownMenuItem asChild>
                                            <Link to="/dashboard" className="cursor-pointer">
                                                <LayoutDashboard className="w-4 h-4 mr-2" />
                                                My Courses
                                            </Link>
                                        </DropdownMenuItem>
                                        {isAdmin && (
                                            <>
                                                <DropdownMenuSeparator />
                                                <DropdownMenuItem asChild>
                                                    <Link to="/admin" className="cursor-pointer">
                                                        <Settings className="w-4 h-4 mr-2" />
                                                        Admin Panel
                                                    </Link>
                                                </DropdownMenuItem>
                                            </>
                                        )}
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem 
                                            onClick={handleLogout}
                                            className="cursor-pointer text-destructive"
                                            data-testid="nav-logout"
                                        >
                                            <LogOut className="w-4 h-4 mr-2" />
                                            Logout
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </div>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link to="/login">
                                    <Button variant="ghost" data-testid="nav-login">
                                        Sign In
                                    </Button>
                                </Link>
                                <Link to="/register">
                                    <Button data-testid="nav-register">
                                        Get Started
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <button 
                        className="md:hidden p-2"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        data-testid="mobile-menu-btn"
                    >
                        <Menu className="w-6 h-6" />
                    </button>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden py-4 border-t border-border">
                        <div className="flex flex-col gap-3">
                            <Link 
                                to="/" 
                                className="px-4 py-2 text-muted-foreground hover:text-foreground"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                Browse Courses
                            </Link>
                            {user ? (
                                <>
                                    <Link 
                                        to="/dashboard" 
                                        className="px-4 py-2 text-muted-foreground hover:text-foreground"
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        Dashboard
                                    </Link>
                                    {isAdmin && (
                                        <Link 
                                            to="/admin" 
                                            className="px-4 py-2 text-muted-foreground hover:text-foreground"
                                            onClick={() => setMobileMenuOpen(false)}
                                        >
                                            Admin Panel
                                        </Link>
                                    )}
                                    <button 
                                        onClick={() => {
                                            handleLogout();
                                            setMobileMenuOpen(false);
                                        }}
                                        className="px-4 py-2 text-left text-destructive"
                                    >
                                        Logout
                                    </button>
                                </>
                            ) : (
                                <>
                                    <Link 
                                        to="/login" 
                                        className="px-4 py-2 text-muted-foreground hover:text-foreground"
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        Sign In
                                    </Link>
                                    <Link 
                                        to="/register"
                                        onClick={() => setMobileMenuOpen(false)}
                                    >
                                        <Button className="mx-4">Get Started</Button>
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
