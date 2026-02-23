import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseApi, paymentApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import { 
    BookOpen, 
    Clock, 
    Users, 
    Star, 
    Play,
    FileText,
    CheckCircle,
    ArrowLeft,
    ShoppingCart,
    Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const CourseDetailsPage = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [purchasing, setPurchasing] = useState(false);

    const isPurchased = user?.purchased_courses?.includes(courseId);

    useEffect(() => {
        fetchCourse();
    }, [courseId]);

    const fetchCourse = async () => {
        try {
            const response = await courseApi.getById(courseId);
            setCourse(response.data);
        } catch (error) {
            toast.error('Failed to load course');
            navigate('/');
        } finally {
            setLoading(false);
        }
    };

    const handlePurchase = async () => {
        if (!user) {
            navigate('/login', { state: { from: `/course/${courseId}` } });
            return;
        }

        if (isPurchased) {
            navigate(`/dashboard/course/${courseId}`);
            return;
        }

        setPurchasing(true);
        try {
            const response = await paymentApi.createCheckout(courseId);
            // Redirect to Stripe checkout
            window.location.href = response.data.checkout_url;
        } catch (error) {
            toast.error(error.message || 'Failed to initiate purchase');
            setPurchasing(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!course) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-heading mb-4">Course not found</h2>
                    <Button onClick={() => navigate('/')}>Back to courses</Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen pb-24">
            {/* Back Button */}
            <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
                <Button 
                    variant="ghost" 
                    onClick={() => navigate('/')}
                    className="gap-2"
                    data-testid="back-btn"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back to courses
                </Button>
            </div>

            {/* Hero Section */}
            <section className="bg-gradient-to-b from-secondary/50 to-background py-12 md:py-16">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="grid lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2">
                            <div className="flex flex-wrap gap-2 mb-4">
                                <Badge variant="secondary">{course.category}</Badge>
                                <Badge variant="outline">{course.level}</Badge>
                            </div>
                            <h1 className="font-heading text-3xl md:text-4xl lg:text-5xl font-normal tracking-tight mb-4" data-testid="course-title">
                                {course.title}
                            </h1>
                            <p className="text-lg text-muted-foreground mb-6">
                                {course.description}
                            </p>
                            <div className="flex flex-wrap items-center gap-6 text-sm">
                                <div className="flex items-center gap-2">
                                    <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
                                    <span className="font-medium">{course.rating.toFixed(1)}</span>
                                    <span className="text-muted-foreground">rating</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Users className="w-5 h-5 text-muted-foreground" />
                                    <span>{course.enrolled_count.toLocaleString()}</span>
                                    <span className="text-muted-foreground">students</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Clock className="w-5 h-5 text-muted-foreground" />
                                    <span>{course.duration_hours} hours</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <BookOpen className="w-5 h-5 text-muted-foreground" />
                                    <span>{course.lessons?.length || 0} lessons</span>
                                </div>
                            </div>
                            <div className="mt-6 flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-medium">
                                    {course.instructor_name?.charAt(0) || 'I'}
                                </div>
                                <div>
                                    <p className="font-medium">{course.instructor_name}</p>
                                    <p className="text-sm text-muted-foreground">Instructor</p>
                                </div>
                            </div>
                        </div>

                        {/* Purchase Card */}
                        <div className="lg:col-span-1">
                            <Card className="sticky top-24 shadow-lg">
                                <div className="relative h-48 overflow-hidden rounded-t-xl">
                                    <img 
                                        src={course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600'}
                                        alt={course.title}
                                        className="w-full h-full object-cover"
                                    />
                                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                                        <div className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center">
                                            <Play className="w-6 h-6 text-primary ml-1" />
                                        </div>
                                    </div>
                                </div>
                                <CardContent className="p-6">
                                    <div className="flex items-baseline gap-2 mb-6">
                                        <span className="font-heading text-4xl font-semibold text-primary">
                                            ${course.price.toFixed(2)}
                                        </span>
                                    </div>
                                    <Button 
                                        className="w-full mb-4 rounded-full py-6 text-lg"
                                        onClick={handlePurchase}
                                        disabled={purchasing}
                                        data-testid="purchase-btn"
                                    >
                                        {purchasing ? (
                                            <>
                                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                                Processing...
                                            </>
                                        ) : isPurchased ? (
                                            <>
                                                <Play className="w-5 h-5 mr-2" />
                                                Continue Learning
                                            </>
                                        ) : (
                                            <>
                                                <ShoppingCart className="w-5 h-5 mr-2" />
                                                Buy Now
                                            </>
                                        )}
                                    </Button>
                                    <div className="space-y-3 text-sm">
                                        <div className="flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4 text-primary" />
                                            <span>Lifetime access</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4 text-primary" />
                                            <span>Certificate of completion</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4 text-primary" />
                                            <span>Downloadable resources</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </section>

            {/* Course Content */}
            <section className="py-12">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <div className="lg:max-w-2xl">
                        <h2 className="font-heading text-2xl md:text-3xl font-medium mb-6">
                            Course Content
                        </h2>
                        <p className="text-muted-foreground mb-6">
                            {course.lessons?.length || 0} lessons • {course.duration_hours} hours total
                        </p>

                        {course.lessons?.length > 0 ? (
                            <Accordion type="single" collapsible className="space-y-3">
                                {course.lessons.map((lesson, index) => (
                                    <AccordionItem 
                                        key={lesson.id} 
                                        value={lesson.id}
                                        className="border rounded-xl px-4"
                                    >
                                        <AccordionTrigger className="hover:no-underline py-4">
                                            <div className="flex items-center gap-4 text-left">
                                                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-sm font-medium">
                                                    {index + 1}
                                                </div>
                                                <div>
                                                    <p className="font-medium">{lesson.title}</p>
                                                    <p className="text-sm text-muted-foreground">
                                                        {lesson.duration_minutes} min
                                                    </p>
                                                </div>
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent className="pb-4">
                                            <p className="text-muted-foreground pl-12">
                                                {lesson.description || 'No description available'}
                                            </p>
                                        </AccordionContent>
                                    </AccordionItem>
                                ))}
                            </Accordion>
                        ) : (
                            <div className="text-center py-8 border rounded-xl">
                                <BookOpen className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
                                <p className="text-muted-foreground">Course content coming soon</p>
                            </div>
                        )}

                        {/* PDF Materials */}
                        {course.pdf_materials?.length > 0 && (
                            <div className="mt-8">
                                <h3 className="font-heading text-xl font-medium mb-4">
                                    Downloadable Resources
                                </h3>
                                <div className="space-y-2">
                                    {course.pdf_materials.map((pdf, index) => (
                                        <div 
                                            key={index}
                                            className="flex items-center gap-3 p-3 border rounded-lg"
                                        >
                                            <FileText className="w-5 h-5 text-primary" />
                                            <span className="flex-1">Resource {index + 1}</span>
                                            <Badge variant="secondary">PDF</Badge>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
};

export default CourseDetailsPage;
