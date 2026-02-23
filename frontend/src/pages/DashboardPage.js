import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { 
    BookOpen, 
    Clock, 
    Play,
    Award,
    Loader2,
    GraduationCap
} from 'lucide-react';
import { toast } from 'sonner';

const DashboardPage = () => {
    const { user } = useAuth();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMyCourses();
    }, []);

    const fetchMyCourses = async () => {
        try {
            const response = await dashboardApi.getMyCourses();
            setCourses(response.data);
        } catch (error) {
            toast.error('Failed to load your courses');
        } finally {
            setLoading(false);
        }
    };

    const completedCourses = courses.filter(c => c.progress >= 100).length;
    const inProgressCourses = courses.filter(c => c.progress > 0 && c.progress < 100).length;
    const totalProgress = courses.length > 0 
        ? Math.round(courses.reduce((sum, c) => sum + c.progress, 0) / courses.length)
        : 0;

    return (
        <div className="min-h-screen bg-background" data-testid="student-dashboard">
            {/* Header */}
            <div className="bg-gradient-to-b from-secondary/50 to-background py-8 md:py-12">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div>
                            <h1 className="font-heading text-3xl md:text-4xl font-normal mb-2">
                                Welcome back, {user?.name?.split(' ')[0]}!
                            </h1>
                            <p className="text-muted-foreground">
                                Continue your learning journey
                            </p>
                        </div>
                        <Link to="/">
                            <Button variant="outline" className="gap-2">
                                <BookOpen className="w-4 h-4" />
                                Browse More Courses
                            </Button>
                        </Link>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <BookOpen className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Enrolled</p>
                                    <p className="text-2xl font-heading font-semibold">{courses.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                                    <Play className="w-6 h-6 text-amber-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">In Progress</p>
                                    <p className="text-2xl font-heading font-semibold">{inProgressCourses}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                                    <Award className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Completed</p>
                                    <p className="text-2xl font-heading font-semibold">{completedCourses}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <GraduationCap className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Avg Progress</p>
                                    <p className="text-2xl font-heading font-semibold">{totalProgress}%</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* My Courses */}
                <div>
                    <h2 className="font-heading text-2xl font-medium mb-6">My Courses</h2>
                    
                    {loading ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-primary" />
                        </div>
                    ) : courses.length === 0 ? (
                        <Card className="text-center py-12">
                            <CardContent>
                                <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                                <h3 className="text-xl font-heading font-medium mb-2">No courses yet</h3>
                                <p className="text-muted-foreground mb-6">
                                    Start your learning journey by enrolling in a course
                                </p>
                                <Link to="/">
                                    <Button>Browse Courses</Button>
                                </Link>
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {courses.map(course => (
                                <Link 
                                    to={`/dashboard/course/${course.id}`} 
                                    key={course.id}
                                    data-testid={`my-course-${course.id}`}
                                >
                                    <Card className="card-hover h-full">
                                        <div className="relative h-40 overflow-hidden rounded-t-xl">
                                            <img 
                                                src={course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400'}
                                                alt={course.title}
                                                className="w-full h-full object-cover"
                                            />
                                            {course.progress >= 100 && (
                                                <div className="absolute top-3 right-3">
                                                    <Badge className="bg-green-500 text-white">
                                                        Completed
                                                    </Badge>
                                                </div>
                                            )}
                                        </div>
                                        <CardContent className="p-5">
                                            <h3 className="font-heading text-lg font-medium mb-2 line-clamp-2">
                                                {course.title}
                                            </h3>
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
                                            <div className="space-y-2">
                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-muted-foreground">Progress</span>
                                                    <span className="font-medium">{Math.round(course.progress)}%</span>
                                                </div>
                                                <Progress value={course.progress} className="h-2" />
                                            </div>
                                            <Button className="w-full mt-4" variant="outline">
                                                <Play className="w-4 h-4 mr-2" />
                                                {course.progress > 0 ? 'Continue' : 'Start'}
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
