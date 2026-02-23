import React, { useState, useEffect } from 'react';
import { courseApi, adminApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '../components/ui/dialog';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../components/ui/select';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../components/ui/table';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { 
    Plus, 
    Upload, 
    Users, 
    BookOpen, 
    DollarSign,
    ShoppingCart,
    Loader2,
    MoreVertical,
    Trash2,
    Edit,
    Video,
    FileText
} from 'lucide-react';
import { toast } from 'sonner';

const AdminPage = () => {
    const [stats, setStats] = useState(null);
    const [courses, setCourses] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [lessonDialogOpen, setLessonDialogOpen] = useState(false);
    const [selectedCourse, setSelectedCourse] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statsRes, coursesRes, usersRes] = await Promise.all([
                adminApi.getStats(),
                courseApi.getAllAdmin(),
                adminApi.getUsers()
            ]);
            setStats(statsRes.data);
            setCourses(coursesRes.data);
            setUsers(usersRes.data);
        } catch (error) {
            toast.error('Failed to load admin data');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteCourse = async (courseId) => {
        if (!window.confirm('Are you sure you want to delete this course?')) return;
        
        try {
            await courseApi.delete(courseId);
            toast.success('Course deleted');
            fetchData();
        } catch (error) {
            toast.error('Failed to delete course');
        }
    };

    const handleUpdateUserRole = async (userId, newRole) => {
        try {
            await adminApi.updateUserRole(userId, newRole);
            toast.success(`User role updated to ${newRole}`);
            fetchData();
        } catch (error) {
            toast.error('Failed to update user role');
        }
    };

    const handleDeleteUser = async (userId) => {
        if (!window.confirm('Are you sure you want to delete this user?')) return;
        
        try {
            await adminApi.deleteUser(userId);
            toast.success('User deleted');
            fetchData();
        } catch (error) {
            toast.error(error.message || 'Failed to delete user');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background" data-testid="admin-panel">
            {/* Header */}
            <div className="bg-gradient-to-b from-secondary/50 to-background py-8">
                <div className="max-w-7xl mx-auto px-4 md:px-8">
                    <h1 className="font-heading text-3xl md:text-4xl font-normal mb-2">
                        Admin Dashboard
                    </h1>
                    <p className="text-muted-foreground">
                        Manage courses, users, and view analytics
                    </p>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <Users className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Total Users</p>
                                    <p className="text-2xl font-heading font-semibold">{stats?.total_users || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                                    <BookOpen className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Courses</p>
                                    <p className="text-2xl font-heading font-semibold">{stats?.total_courses || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                                    <ShoppingCart className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Purchases</p>
                                    <p className="text-2xl font-heading font-semibold">{stats?.total_purchases || 0}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                                    <DollarSign className="w-6 h-6 text-amber-600" />
                                </div>
                                <div>
                                    <p className="text-sm text-muted-foreground">Revenue</p>
                                    <p className="text-2xl font-heading font-semibold">${stats?.total_revenue?.toFixed(2) || '0.00'}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Tabs */}
                <Tabs defaultValue="courses">
                    <TabsList>
                        <TabsTrigger value="courses">Courses</TabsTrigger>
                        <TabsTrigger value="users">Users</TabsTrigger>
                        <TabsTrigger value="transactions">Transactions</TabsTrigger>
                    </TabsList>

                    {/* Courses Tab */}
                    <TabsContent value="courses" className="mt-6">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="font-heading text-xl font-medium">All Courses</h2>
                            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button className="gap-2" data-testid="create-course-btn">
                                        <Plus className="w-4 h-4" />
                                        Create Course
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                                    <DialogHeader>
                                        <DialogTitle>Create New Course</DialogTitle>
                                        <DialogDescription>
                                            Fill in the details to create a new course
                                        </DialogDescription>
                                    </DialogHeader>
                                    <CreateCourseForm 
                                        onSuccess={() => {
                                            setCreateDialogOpen(false);
                                            fetchData();
                                        }} 
                                    />
                                </DialogContent>
                            </Dialog>
                        </div>

                        <div className="rounded-lg border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Course</TableHead>
                                        <TableHead>Category</TableHead>
                                        <TableHead>Price</TableHead>
                                        <TableHead>Enrolled</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead className="w-[100px]">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {courses.map(course => (
                                        <TableRow key={course.id}>
                                            <TableCell>
                                                <div className="flex items-center gap-3">
                                                    <img 
                                                        src={course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=100'}
                                                        alt={course.title}
                                                        className="w-12 h-12 rounded-lg object-cover"
                                                    />
                                                    <div>
                                                        <p className="font-medium line-clamp-1">{course.title}</p>
                                                        <p className="text-sm text-muted-foreground">
                                                            {course.lessons_count} lessons
                                                        </p>
                                                    </div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline">{course.category}</Badge>
                                            </TableCell>
                                            <TableCell>${course.price.toFixed(2)}</TableCell>
                                            <TableCell>{course.enrolled_count}</TableCell>
                                            <TableCell>
                                                <Badge variant={course.is_published !== false ? 'default' : 'secondary'}>
                                                    {course.is_published !== false ? 'Published' : 'Draft'}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" size="icon">
                                                            <MoreVertical className="w-4 h-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem
                                                            onClick={() => {
                                                                setSelectedCourse(course);
                                                                setLessonDialogOpen(true);
                                                            }}
                                                        >
                                                            <Video className="w-4 h-4 mr-2" />
                                                            Add Lesson
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => {
                                                                const input = document.createElement('input');
                                                                input.type = 'file';
                                                                input.accept = '.pdf';
                                                                input.onchange = async (e) => {
                                                                    const file = e.target.files[0];
                                                                    if (file) {
                                                                        try {
                                                                            await courseApi.uploadPdf(course.id, file);
                                                                            toast.success('PDF uploaded successfully');
                                                                            fetchData();
                                                                        } catch (error) {
                                                                            toast.error('Failed to upload PDF');
                                                                        }
                                                                    }
                                                                };
                                                                input.click();
                                                            }}
                                                        >
                                                            <FileText className="w-4 h-4 mr-2" />
                                                            Upload PDF
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => handleDeleteCourse(course.id)}
                                                            className="text-destructive"
                                                        >
                                                            <Trash2 className="w-4 h-4 mr-2" />
                                                            Delete
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>

                    {/* Users Tab */}
                    <TabsContent value="users" className="mt-6">
                        <h2 className="font-heading text-xl font-medium mb-6">All Users</h2>
                        <div className="rounded-lg border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>User</TableHead>
                                        <TableHead>Email</TableHead>
                                        <TableHead>Role</TableHead>
                                        <TableHead>Courses</TableHead>
                                        <TableHead>Joined</TableHead>
                                        <TableHead className="w-[100px]">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {users.map(user => (
                                        <TableRow key={user.id}>
                                            <TableCell>
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-medium">
                                                        {user.name?.charAt(0) || 'U'}
                                                    </div>
                                                    <span className="font-medium">{user.name}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell>{user.email}</TableCell>
                                            <TableCell>
                                                <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                                                    {user.role}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{user.purchased_courses?.length || 0}</TableCell>
                                            <TableCell>
                                                {new Date(user.created_at).toLocaleDateString()}
                                            </TableCell>
                                            <TableCell>
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" size="icon">
                                                            <MoreVertical className="w-4 h-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem
                                                            onClick={() => handleUpdateUserRole(
                                                                user.id, 
                                                                user.role === 'admin' ? 'student' : 'admin'
                                                            )}
                                                        >
                                                            <Edit className="w-4 h-4 mr-2" />
                                                            Make {user.role === 'admin' ? 'Student' : 'Admin'}
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() => handleDeleteUser(user.id)}
                                                            className="text-destructive"
                                                        >
                                                            <Trash2 className="w-4 h-4 mr-2" />
                                                            Delete
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>

                    {/* Transactions Tab */}
                    <TabsContent value="transactions" className="mt-6">
                        <h2 className="font-heading text-xl font-medium mb-6">Recent Transactions</h2>
                        <div className="rounded-lg border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>User</TableHead>
                                        <TableHead>Course</TableHead>
                                        <TableHead>Amount</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Date</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {stats?.recent_transactions?.map((tx, idx) => (
                                        <TableRow key={idx}>
                                            <TableCell>{tx.user_email}</TableCell>
                                            <TableCell>{tx.metadata?.course_title || tx.course_id}</TableCell>
                                            <TableCell>${tx.amount?.toFixed(2)}</TableCell>
                                            <TableCell>
                                                <Badge variant={
                                                    tx.payment_status === 'paid' ? 'default' : 
                                                    tx.payment_status === 'failed' ? 'destructive' : 
                                                    'secondary'
                                                }>
                                                    {tx.payment_status}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                {new Date(tx.created_at).toLocaleDateString()}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {(!stats?.recent_transactions || stats.recent_transactions.length === 0) && (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                                No transactions yet
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>
                </Tabs>
            </div>

            {/* Add Lesson Dialog */}
            <Dialog open={lessonDialogOpen} onOpenChange={setLessonDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Add Lesson to {selectedCourse?.title}</DialogTitle>
                        <DialogDescription>
                            Add a new lesson with YouTube video
                        </DialogDescription>
                    </DialogHeader>
                    <AddLessonForm 
                        courseId={selectedCourse?.id}
                        onSuccess={() => {
                            setLessonDialogOpen(false);
                            fetchData();
                        }} 
                    />
                </DialogContent>
            </Dialog>
        </div>
    );
};

// Create Course Form Component
const CreateCourseForm = ({ onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        short_description: '',
        price: '',
        thumbnail_url: '',
        category: 'Web Development',
        level: 'Beginner',
        duration_hours: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            await courseApi.create({
                ...formData,
                price: parseFloat(formData.price),
                duration_hours: parseInt(formData.duration_hours) || 0
            });
            toast.success('Course created successfully');
            onSuccess();
        } catch (error) {
            toast.error(error.message || 'Failed to create course');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
                <Label htmlFor="title">Course Title</Label>
                <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Complete React Course"
                    required
                    data-testid="course-title-input"
                />
            </div>
            
            <div className="space-y-2">
                <Label htmlFor="short_description">Short Description</Label>
                <Input
                    id="short_description"
                    value={formData.short_description}
                    onChange={(e) => setFormData(prev => ({ ...prev, short_description: e.target.value }))}
                    placeholder="Brief description for course cards"
                    required
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="description">Full Description</Label>
                <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Detailed course description"
                    rows={4}
                    required
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label htmlFor="price">Price ($)</Label>
                    <Input
                        id="price"
                        type="number"
                        step="0.01"
                        min="0"
                        value={formData.price}
                        onChange={(e) => setFormData(prev => ({ ...prev, price: e.target.value }))}
                        placeholder="49.99"
                        required
                        data-testid="course-price-input"
                    />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="duration">Duration (hours)</Label>
                    <Input
                        id="duration"
                        type="number"
                        min="0"
                        value={formData.duration_hours}
                        onChange={(e) => setFormData(prev => ({ ...prev, duration_hours: e.target.value }))}
                        placeholder="10"
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label>Category</Label>
                    <Select 
                        value={formData.category}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
                    >
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Web Development">Web Development</SelectItem>
                            <SelectItem value="Data Science">Data Science</SelectItem>
                            <SelectItem value="Design">Design</SelectItem>
                            <SelectItem value="Business">Business</SelectItem>
                            <SelectItem value="Marketing">Marketing</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="space-y-2">
                    <Label>Level</Label>
                    <Select 
                        value={formData.level}
                        onValueChange={(value) => setFormData(prev => ({ ...prev, level: value }))}
                    >
                        <SelectTrigger>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="Beginner">Beginner</SelectItem>
                            <SelectItem value="Intermediate">Intermediate</SelectItem>
                            <SelectItem value="Advanced">Advanced</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="space-y-2">
                <Label htmlFor="thumbnail">Thumbnail URL</Label>
                <Input
                    id="thumbnail"
                    value={formData.thumbnail_url}
                    onChange={(e) => setFormData(prev => ({ ...prev, thumbnail_url: e.target.value }))}
                    placeholder="https://example.com/image.jpg"
                />
            </div>

            <Button type="submit" className="w-full" disabled={loading} data-testid="submit-course-btn">
                {loading ? (
                    <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Creating...
                    </>
                ) : (
                    'Create Course'
                )}
            </Button>
        </form>
    );
};

// Add Lesson Form Component
const AddLessonForm = ({ courseId, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        video_url: '',
        duration_minutes: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!courseId) return;
        
        setLoading(true);
        
        try {
            const data = new FormData();
            data.append('title', formData.title);
            data.append('description', formData.description);
            data.append('video_url', formData.video_url);
            data.append('duration_minutes', formData.duration_minutes || '0');
            
            await courseApi.addLesson(courseId, data);
            toast.success('Lesson added successfully');
            onSuccess();
        } catch (error) {
            toast.error(error.message || 'Failed to add lesson');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
                <Label htmlFor="lesson-title">Lesson Title</Label>
                <Input
                    id="lesson-title"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Introduction to React"
                    required
                    data-testid="lesson-title-input"
                />
            </div>
            
            <div className="space-y-2">
                <Label htmlFor="lesson-description">Description</Label>
                <Textarea
                    id="lesson-description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="What will students learn in this lesson?"
                    rows={3}
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="video-url">YouTube Video URL</Label>
                <Input
                    id="video-url"
                    value={formData.video_url}
                    onChange={(e) => setFormData(prev => ({ ...prev, video_url: e.target.value }))}
                    placeholder="https://www.youtube.com/watch?v=..."
                    required
                    data-testid="lesson-video-input"
                />
            </div>

            <div className="space-y-2">
                <Label htmlFor="lesson-duration">Duration (minutes)</Label>
                <Input
                    id="lesson-duration"
                    type="number"
                    min="0"
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData(prev => ({ ...prev, duration_minutes: e.target.value }))}
                    placeholder="15"
                />
            </div>

            <Button type="submit" className="w-full" disabled={loading} data-testid="submit-lesson-btn">
                {loading ? (
                    <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Adding...
                    </>
                ) : (
                    'Add Lesson'
                )}
            </Button>
        </form>
    );
};

export default AdminPage;
