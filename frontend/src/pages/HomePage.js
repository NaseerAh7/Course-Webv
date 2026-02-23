import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { courseApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { 
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue 
} from '../components/ui/select';
import { 
    BookOpen, 
    Clock, 
    Users, 
    Star, 
    Search,
    ArrowRight,
    Play,
    Award,
    Zap
} from 'lucide-react';
import { toast } from 'sonner';

const HomePage = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [levelFilter, setLevelFilter] = useState('all');

    useEffect(() => {
        fetchCourses();
    }, []);

    const fetchCourses = async () => {
        try {
            const response = await courseApi.getAll();
            setCourses(response.data);
        } catch (error) {
            toast.error('Failed to load courses');
        } finally {
            setLoading(false);
        }
    };

    const filteredCourses = courses.filter(course => {
        const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             course.short_description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = categoryFilter === 'all' || course.category === categoryFilter;
        const matchesLevel = levelFilter === 'all' || course.level === levelFilter;
        return matchesSearch && matchesCategory && matchesLevel;
    });

    const categories = [...new Set(courses.map(c => c.category))];
    const levels = ['Beginner', 'Intermediate', 'Advanced'];

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative overflow-hidden bg-gradient-to-b from-secondary/50 to-background py-24 md:py-32">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        <div className="animate-fade-in">
                            <Badge className="mb-6 bg-primary/10 text-primary hover:bg-primary/20 border-0">
                                <Zap className="w-3 h-3 mr-1" />
                                Learn from Industry Experts
                            </Badge>
                            <h1 className="font-heading text-5xl md:text-7xl font-light tracking-tight leading-[0.9] text-foreground mb-6">
                                Master New Skills,{' '}
                                <span className="gradient-text">Transform</span> Your Career
                            </h1>
                            <p className="text-lg md:text-xl text-muted-foreground leading-relaxed mb-8 max-w-lg">
                                Access high-quality courses taught by industry professionals. 
                                Learn at your own pace with lifetime access.
                            </p>
                            <div className="flex flex-wrap gap-4">
                                <Link to="#courses">
                                    <Button 
                                        size="lg" 
                                        className="rounded-full px-8 py-6 shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all"
                                        data-testid="hero-browse-btn"
                                    >
                                        Browse Courses
                                        <ArrowRight className="ml-2 w-4 h-4" />
                                    </Button>
                                </Link>
                                <Link to="/register">
                                    <Button 
                                        variant="outline" 
                                        size="lg" 
                                        className="rounded-full px-8 py-6"
                                        data-testid="hero-signup-btn"
                                    >
                                        Start Free
                                    </Button>
                                </Link>
                            </div>
                        </div>
                        <div className="relative animate-fade-in animation-delay-200">
                            <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                                <img 
                                    src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800"
                                    alt="Learning"
                                    className="w-full h-[400px] object-cover"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                                <div className="absolute bottom-6 left-6 right-6">
                                    <div className="flex items-center gap-3 text-white">
                                        <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                                            <Play className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="font-medium">Watch Preview</p>
                                            <p className="text-sm text-white/70">See what you'll learn</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-16 border-b border-border">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { value: '10K+', label: 'Students', icon: Users },
                            { value: '50+', label: 'Courses', icon: BookOpen },
                            { value: '4.8', label: 'Avg Rating', icon: Star },
                            { value: '100%', label: 'Satisfaction', icon: Award }
                        ].map((stat, index) => (
                            <div 
                                key={index} 
                                className="text-center animate-fade-in"
                                style={{ animationDelay: `${index * 100}ms` }}
                            >
                                <stat.icon className="w-8 h-8 mx-auto mb-3 text-primary" />
                                <p className="font-heading text-3xl md:text-4xl font-semibold text-foreground">
                                    {stat.value}
                                </p>
                                <p className="text-muted-foreground">{stat.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Courses Section */}
            <section id="courses" className="py-24 md:py-32">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="text-center mb-12">
                        <h2 className="font-heading text-4xl md:text-5xl font-normal tracking-tight mb-4">
                            Featured Courses
                        </h2>
                        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                            Explore our curated selection of courses designed to help you succeed
                        </p>
                    </div>

                    {/* Filters */}
                    <div className="flex flex-wrap gap-4 mb-12">
                        <div className="relative flex-1 min-w-[200px]">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                            <Input
                                placeholder="Search courses..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-10"
                                data-testid="search-input"
                            />
                        </div>
                        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                            <SelectTrigger className="w-[180px]" data-testid="category-filter">
                                <SelectValue placeholder="Category" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Categories</SelectItem>
                                {categories.map(cat => (
                                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select value={levelFilter} onValueChange={setLevelFilter}>
                            <SelectTrigger className="w-[180px]" data-testid="level-filter">
                                <SelectValue placeholder="Level" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Levels</SelectItem>
                                {levels.map(level => (
                                    <SelectItem key={level} value={level}>{level}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Course Grid */}
                    {loading ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                            {[1, 2, 3, 4].map(i => (
                                <Card key={i} className="animate-pulse">
                                    <div className="h-48 bg-muted rounded-t-xl" />
                                    <CardContent className="p-6">
                                        <div className="h-4 bg-muted rounded w-1/2 mb-4" />
                                        <div className="h-6 bg-muted rounded mb-2" />
                                        <div className="h-4 bg-muted rounded w-3/4" />
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : filteredCourses.length === 0 ? (
                        <div className="text-center py-12">
                            <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-xl font-medium mb-2">No courses found</h3>
                            <p className="text-muted-foreground">Try adjusting your search or filters</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                            {filteredCourses.map((course, index) => (
                                <Link 
                                    to={`/course/${course.id}`} 
                                    key={course.id}
                                    className="animate-fade-in block"
                                    style={{ animationDelay: `${index * 50}ms` }}
                                    data-testid={`course-card-${course.id}`}
                                >
                                    <Card className="card-hover overflow-hidden group h-full">
                                        <div className="relative h-48 overflow-hidden">
                                            <img 
                                                src={course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400'}
                                                alt={course.title}
                                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                            />
                                            <div className="absolute top-3 left-3">
                                                <Badge variant="secondary" className="backdrop-blur bg-white/90">
                                                    {course.level}
                                                </Badge>
                                            </div>
                                        </div>
                                        <CardContent className="p-6">
                                            <Badge variant="outline" className="mb-3 text-xs">
                                                {course.category}
                                            </Badge>
                                            <h3 className="font-heading text-lg font-medium mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                                                {course.title}
                                            </h3>
                                            <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                                                {course.short_description}
                                            </p>
                                            <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                                                <span className="flex items-center gap-1">
                                                    <Clock className="w-4 h-4" />
                                                    {course.duration_hours}h
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <BookOpen className="w-4 h-4" />
                                                    {course.lessons_count} lessons
                                                </span>
                                            </div>
                                            <div className="flex items-center justify-between pt-4 border-t border-border">
                                                <div className="flex items-center gap-1">
                                                    <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                                                    <span className="font-medium">{course.rating.toFixed(1)}</span>
                                                    <span className="text-muted-foreground">({course.enrolled_count})</span>
                                                </div>
                                                <span className="font-heading text-xl font-semibold text-primary">
                                                    ${course.price.toFixed(2)}
                                                </span>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 bg-primary text-primary-foreground">
                <div className="max-w-4xl mx-auto px-4 md:px-8 text-center">
                    <h2 className="font-heading text-4xl md:text-5xl font-normal mb-6">
                        Ready to Start Learning?
                    </h2>
                    <p className="text-lg opacity-90 mb-8 max-w-2xl mx-auto">
                        Join thousands of students who are already transforming their careers with our courses.
                    </p>
                    <Link to="/register">
                        <Button 
                            size="lg" 
                            variant="secondary"
                            className="rounded-full px-8 py-6 text-lg"
                            data-testid="cta-signup-btn"
                        >
                            Create Free Account
                            <ArrowRight className="ml-2 w-5 h-5" />
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-border">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                                <BookOpen className="w-4 h-4 text-primary-foreground" />
                            </div>
                            <span className="font-heading font-semibold">CourseHub</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            © 2024 CourseHub. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default HomePage;
