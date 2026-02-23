import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dashboardApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';
import { ScrollArea } from '../components/ui/scroll-area';
import { 
    ArrowLeft,
    Play,
    CheckCircle,
    FileText,
    Download,
    Loader2,
    BookOpen
} from 'lucide-react';
import { toast } from 'sonner';

const CoursePlayerPage = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [course, setCourse] = useState(null);
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeLesson, setActiveLesson] = useState(null);
    const [updatingProgress, setUpdatingProgress] = useState(false);

    useEffect(() => {
        fetchCourseContent();
    }, [courseId]);

    const fetchCourseContent = async () => {
        try {
            const response = await dashboardApi.getCourseContent(courseId);
            setCourse(response.data.course);
            setProgress(response.data.progress);
            
            // Set initial active lesson
            const lessons = response.data.course.lessons || [];
            if (lessons.length > 0) {
                const lastLessonId = response.data.progress?.last_lesson_id;
                const lastLesson = lessons.find(l => l.id === lastLessonId);
                setActiveLesson(lastLesson || lessons[0]);
            }
        } catch (error) {
            toast.error('You do not have access to this course');
            navigate('/dashboard');
        } finally {
            setLoading(false);
        }
    };

    const handleLessonComplete = async (lessonId, completed) => {
        setUpdatingProgress(true);
        try {
            const response = await dashboardApi.updateProgress(courseId, {
                lesson_id: lessonId,
                completed
            });
            
            // Update local progress state
            setProgress(prev => ({
                ...prev,
                completed_lessons: completed 
                    ? [...(prev.completed_lessons || []), lessonId]
                    : (prev.completed_lessons || []).filter(id => id !== lessonId),
                progress_percentage: response.data.progress_percentage
            }));
            
            toast.success(completed ? 'Lesson marked as complete!' : 'Lesson unmarked');
        } catch (error) {
            toast.error('Failed to update progress');
        } finally {
            setUpdatingProgress(false);
        }
    };

    const handleDownloadPdf = async (index) => {
        try {
            const response = await dashboardApi.downloadPdf(courseId, index);
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `resource-${index + 1}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            toast.error('Failed to download PDF');
        }
    };

    const isLessonCompleted = (lessonId) => {
        return progress?.completed_lessons?.includes(lessonId);
    };

    // Convert YouTube URL to embed URL
    const getEmbedUrl = (url) => {
        if (!url) return '';
        
        // Already an embed URL
        if (url.includes('/embed/')) return url;
        
        // Extract video ID from various YouTube URL formats
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        
        if (match && match[2].length === 11) {
            return `https://www.youtube.com/embed/${match[2]}`;
        }
        
        return url;
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
                    <BookOpen className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                    <h2 className="text-2xl font-heading mb-4">Course not found</h2>
                    <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background" data-testid="course-player">
            {/* Header */}
            <div className="border-b bg-card">
                <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Button 
                                variant="ghost" 
                                size="icon"
                                onClick={() => navigate('/dashboard')}
                                data-testid="back-to-dashboard"
                            >
                                <ArrowLeft className="w-5 h-5" />
                            </Button>
                            <div>
                                <h1 className="font-heading text-lg font-medium line-clamp-1">
                                    {course.title}
                                </h1>
                                <p className="text-sm text-muted-foreground">
                                    {course.lessons?.length || 0} lessons
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="hidden md:flex items-center gap-3">
                                <span className="text-sm text-muted-foreground">
                                    {Math.round(progress?.progress_percentage || 0)}% complete
                                </span>
                                <Progress 
                                    value={progress?.progress_percentage || 0} 
                                    className="w-32 h-2" 
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row">
                {/* Video Player */}
                <div className="flex-1">
                    <div className="video-cinema-mode">
                        <div className="aspect-video w-full">
                            {activeLesson?.video_url ? (
                                <iframe
                                    src={getEmbedUrl(activeLesson.video_url)}
                                    title={activeLesson.title}
                                    className="w-full h-full"
                                    frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                    data-testid="video-player"
                                />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center bg-muted">
                                    <p className="text-muted-foreground">No video available</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Lesson Info */}
                    <div className="p-6 md:p-8">
                        <div className="flex items-start justify-between gap-4 mb-4">
                            <div>
                                <h2 className="font-heading text-2xl font-medium mb-2">
                                    {activeLesson?.title}
                                </h2>
                                <p className="text-muted-foreground">
                                    {activeLesson?.description}
                                </p>
                            </div>
                            <div className="flex items-center gap-2">
                                <Checkbox
                                    id="complete-lesson"
                                    checked={isLessonCompleted(activeLesson?.id)}
                                    onCheckedChange={(checked) => 
                                        handleLessonComplete(activeLesson?.id, checked)
                                    }
                                    disabled={updatingProgress}
                                    data-testid="mark-complete-checkbox"
                                />
                                <label 
                                    htmlFor="complete-lesson" 
                                    className="text-sm cursor-pointer"
                                >
                                    Mark as complete
                                </label>
                            </div>
                        </div>

                        {/* PDF Materials */}
                        {course.pdf_materials?.length > 0 && (
                            <div className="mt-8">
                                <h3 className="font-heading text-lg font-medium mb-4">
                                    Course Materials
                                </h3>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {course.pdf_materials.map((pdf, index) => (
                                        <Card key={index}>
                                            <CardContent className="p-4 flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <FileText className="w-5 h-5 text-primary" />
                                                    <span className="font-medium">Resource {index + 1}</span>
                                                </div>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handleDownloadPdf(index)}
                                                    data-testid={`download-pdf-${index}`}
                                                >
                                                    <Download className="w-4 h-4" />
                                                </Button>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Lesson Sidebar */}
                <div className="lg:w-96 border-l bg-card">
                    <div className="p-4 border-b">
                        <h3 className="font-heading font-medium">Course Content</h3>
                    </div>
                    <ScrollArea className="h-[calc(100vh-200px)]">
                        <div className="p-2">
                            {course.lessons?.map((lesson, index) => {
                                const isActive = activeLesson?.id === lesson.id;
                                const isCompleted = isLessonCompleted(lesson.id);
                                
                                return (
                                    <button
                                        key={lesson.id}
                                        onClick={() => setActiveLesson(lesson)}
                                        className={`w-full p-4 rounded-lg text-left transition-colors mb-1 ${
                                            isActive 
                                                ? 'bg-primary/10 border border-primary/20' 
                                                : 'hover:bg-muted'
                                        }`}
                                        data-testid={`lesson-${lesson.id}`}
                                    >
                                        <div className="flex items-start gap-3">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                                                isCompleted 
                                                    ? 'bg-green-100 text-green-600'
                                                    : isActive
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-muted text-muted-foreground'
                                            }`}>
                                                {isCompleted ? (
                                                    <CheckCircle className="w-4 h-4" />
                                                ) : isActive ? (
                                                    <Play className="w-4 h-4" />
                                                ) : (
                                                    <span className="text-sm">{index + 1}</span>
                                                )}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className={`font-medium text-sm line-clamp-2 ${
                                                    isActive ? 'text-primary' : ''
                                                }`}>
                                                    {lesson.title}
                                                </p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    {lesson.duration_minutes} min
                                                </p>
                                            </div>
                                            {isCompleted && (
                                                <Badge variant="secondary" className="text-xs">
                                                    Done
                                                </Badge>
                                            )}
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    </ScrollArea>
                </div>
            </div>
        </div>
    );
};

export default CoursePlayerPage;
