import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { BookOpen, Loader2, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const RegisterPage = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [errors, setErrors] = useState({});

    const validate = () => {
        const newErrors = {};
        if (!formData.name || formData.name.length < 2) {
            newErrors.name = 'Name must be at least 2 characters';
        }
        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Invalid email format';
        }
        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) return;

        setLoading(true);
        try {
            await register(formData.name, formData.email, formData.password);
            toast.success('Account created successfully!');
            navigate('/dashboard');
        } catch (error) {
            toast.error(error.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const passwordStrength = () => {
        const password = formData.password;
        if (!password) return 0;
        let strength = 0;
        if (password.length >= 6) strength++;
        if (password.length >= 8) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        return strength;
    };

    const strength = passwordStrength();

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-secondary/30 to-background px-4 py-12">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <Link to="/" className="inline-flex items-center gap-2 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
                            <BookOpen className="w-6 h-6 text-primary-foreground" />
                        </div>
                    </Link>
                    <h1 className="font-heading text-3xl font-semibold mb-2">Create an account</h1>
                    <p className="text-muted-foreground">
                        Start your learning journey today
                    </p>
                </div>

                <Card className="shadow-lg">
                    <CardHeader className="pb-4">
                        <CardTitle>Sign Up</CardTitle>
                        <CardDescription>
                            Fill in your details to create your account
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Full Name</Label>
                                <Input
                                    id="name"
                                    name="name"
                                    type="text"
                                    placeholder="John Doe"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className={errors.name ? 'border-destructive' : ''}
                                    data-testid="register-name"
                                />
                                {errors.name && (
                                    <p className="text-sm text-destructive">{errors.name}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    name="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className={errors.email ? 'border-destructive' : ''}
                                    data-testid="register-email"
                                />
                                {errors.email && (
                                    <p className="text-sm text-destructive">{errors.email}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <div className="relative">
                                    <Input
                                        id="password"
                                        name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        placeholder="••••••••"
                                        value={formData.password}
                                        onChange={handleChange}
                                        className={errors.password ? 'border-destructive pr-10' : 'pr-10'}
                                        data-testid="register-password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                    >
                                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                                {formData.password && (
                                    <div className="flex gap-1 mt-2">
                                        {[1, 2, 3, 4, 5].map(level => (
                                            <div
                                                key={level}
                                                className={`h-1 flex-1 rounded-full ${
                                                    level <= strength
                                                        ? strength <= 2
                                                            ? 'bg-destructive'
                                                            : strength <= 3
                                                            ? 'bg-amber-500'
                                                            : 'bg-green-500'
                                                        : 'bg-muted'
                                                }`}
                                            />
                                        ))}
                                    </div>
                                )}
                                {errors.password && (
                                    <p className="text-sm text-destructive">{errors.password}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="confirmPassword">Confirm Password</Label>
                                <Input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    placeholder="••••••••"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className={errors.confirmPassword ? 'border-destructive' : ''}
                                    data-testid="register-confirm-password"
                                />
                                {errors.confirmPassword && (
                                    <p className="text-sm text-destructive">{errors.confirmPassword}</p>
                                )}
                            </div>

                            <Button 
                                type="submit" 
                                className="w-full" 
                                disabled={loading}
                                data-testid="register-submit"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Creating account...
                                    </>
                                ) : (
                                    'Create Account'
                                )}
                            </Button>
                        </form>

                        <div className="mt-6">
                            <div className="space-y-2 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-primary" />
                                    <span>Free access to course previews</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-primary" />
                                    <span>Track your learning progress</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-primary" />
                                    <span>Get personalized recommendations</span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 text-center text-sm">
                            <span className="text-muted-foreground">Already have an account? </span>
                            <Link to="/login" className="text-primary hover:underline font-medium">
                                Sign in
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default RegisterPage;
