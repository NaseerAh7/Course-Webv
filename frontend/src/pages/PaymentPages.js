import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { paymentApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { CheckCircle, XCircle, Loader2, ArrowRight, RefreshCw } from 'lucide-react';

const PaymentSuccessPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { refreshUser } = useAuth();
    const [status, setStatus] = useState('loading'); // loading, success, pending, error
    const [courseId, setCourseId] = useState(null);
    const [pollCount, setPollCount] = useState(0);

    const sessionId = searchParams.get('session_id');
    const maxPolls = 5;
    const pollInterval = 2000;

    useEffect(() => {
        if (sessionId) {
            pollPaymentStatus();
        } else {
            setStatus('error');
        }
    }, [sessionId]);

    const pollPaymentStatus = async () => {
        if (pollCount >= maxPolls) {
            setStatus('pending');
            return;
        }

        try {
            const response = await paymentApi.getStatus(sessionId);
            const { payment_status, course_id } = response.data;
            
            setCourseId(course_id);

            if (payment_status === 'paid') {
                setStatus('success');
                // Refresh user data to get updated purchased courses
                await refreshUser();
                return;
            } else if (payment_status === 'expired' || payment_status === 'failed') {
                setStatus('error');
                return;
            }

            // Continue polling
            setPollCount(prev => prev + 1);
            setTimeout(pollPaymentStatus, pollInterval);
        } catch (error) {
            console.error('Error checking payment status:', error);
            setStatus('error');
        }
    };

    const handleRetry = () => {
        setPollCount(0);
        setStatus('loading');
        pollPaymentStatus();
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-secondary/30 to-background px-4" data-testid="payment-success-page">
            <Card className="max-w-md w-full shadow-lg">
                <CardContent className="p-8 text-center">
                    {status === 'loading' && (
                        <>
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-primary/10 flex items-center justify-center">
                                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            </div>
                            <h1 className="font-heading text-2xl font-semibold mb-2">
                                Processing Payment
                            </h1>
                            <p className="text-muted-foreground mb-6">
                                Please wait while we confirm your payment...
                            </p>
                            <div className="text-sm text-muted-foreground">
                                Attempt {pollCount + 1} of {maxPolls}
                            </div>
                        </>
                    )}

                    {status === 'success' && (
                        <>
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-green-100 flex items-center justify-center">
                                <CheckCircle className="w-8 h-8 text-green-600" />
                            </div>
                            <h1 className="font-heading text-2xl font-semibold mb-2">
                                Payment Successful!
                            </h1>
                            <p className="text-muted-foreground mb-6">
                                Thank you for your purchase. You now have access to the course.
                            </p>
                            <div className="space-y-3">
                                {courseId && (
                                    <Button 
                                        className="w-full" 
                                        onClick={() => navigate(`/dashboard/course/${courseId}`)}
                                        data-testid="start-learning-btn"
                                    >
                                        Start Learning
                                        <ArrowRight className="w-4 h-4 ml-2" />
                                    </Button>
                                )}
                                <Button 
                                    variant="outline" 
                                    className="w-full"
                                    onClick={() => navigate('/dashboard')}
                                >
                                    Go to Dashboard
                                </Button>
                            </div>
                        </>
                    )}

                    {status === 'pending' && (
                        <>
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-amber-100 flex items-center justify-center">
                                <Loader2 className="w-8 h-8 text-amber-600" />
                            </div>
                            <h1 className="font-heading text-2xl font-semibold mb-2">
                                Payment Processing
                            </h1>
                            <p className="text-muted-foreground mb-6">
                                Your payment is still being processed. This may take a few moments.
                            </p>
                            <div className="space-y-3">
                                <Button onClick={handleRetry} className="w-full gap-2">
                                    <RefreshCw className="w-4 h-4" />
                                    Check Again
                                </Button>
                                <Button 
                                    variant="outline" 
                                    className="w-full"
                                    onClick={() => navigate('/dashboard')}
                                >
                                    Go to Dashboard
                                </Button>
                            </div>
                            <p className="text-xs text-muted-foreground mt-4">
                                If you've been charged, the course will appear in your dashboard shortly.
                            </p>
                        </>
                    )}

                    {status === 'error' && (
                        <>
                            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-destructive/10 flex items-center justify-center">
                                <XCircle className="w-8 h-8 text-destructive" />
                            </div>
                            <h1 className="font-heading text-2xl font-semibold mb-2">
                                Payment Failed
                            </h1>
                            <p className="text-muted-foreground mb-6">
                                Something went wrong with your payment. Please try again.
                            </p>
                            <div className="space-y-3">
                                <Button 
                                    className="w-full"
                                    onClick={() => navigate('/')}
                                >
                                    Browse Courses
                                </Button>
                                <Button 
                                    variant="outline" 
                                    className="w-full"
                                    onClick={() => navigate('/dashboard')}
                                >
                                    Go to Dashboard
                                </Button>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

const PaymentCancelPage = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-secondary/30 to-background px-4" data-testid="payment-cancel-page">
            <Card className="max-w-md w-full shadow-lg">
                <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-muted flex items-center justify-center">
                        <XCircle className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h1 className="font-heading text-2xl font-semibold mb-2">
                        Payment Cancelled
                    </h1>
                    <p className="text-muted-foreground mb-6">
                        Your payment was cancelled. No charges have been made.
                    </p>
                    <div className="space-y-3">
                        <Button 
                            className="w-full"
                            onClick={() => navigate('/')}
                        >
                            Browse Courses
                        </Button>
                        <Button 
                            variant="outline" 
                            className="w-full"
                            onClick={() => navigate('/dashboard')}
                        >
                            Go to Dashboard
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export { PaymentSuccessPage, PaymentCancelPage };
