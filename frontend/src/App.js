import "@/App.css";
import "@/index.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";

// Pages
import HomePage from "./pages/HomePage";
import CourseDetailsPage from "./pages/CourseDetailsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import CoursePlayerPage from "./pages/CoursePlayerPage";
import AdminPage from "./pages/AdminPage";
import { PaymentSuccessPage, PaymentCancelPage } from "./pages/PaymentPages";

// Layout wrapper for pages with navbar
const MainLayout = ({ children }) => (
    <>
        <Navbar />
        {children}
    </>
);

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public routes */}
                    <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
                    <Route path="/course/:courseId" element={<MainLayout><CourseDetailsPage /></MainLayout>} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    
                    {/* Payment routes */}
                    <Route path="/payment/success" element={
                        <ProtectedRoute>
                            <PaymentSuccessPage />
                        </ProtectedRoute>
                    } />
                    <Route path="/payment/cancel" element={
                        <ProtectedRoute>
                            <PaymentCancelPage />
                        </ProtectedRoute>
                    } />
                    
                    {/* Protected routes */}
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <MainLayout><DashboardPage /></MainLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/dashboard/course/:courseId" element={
                        <ProtectedRoute>
                            <CoursePlayerPage />
                        </ProtectedRoute>
                    } />
                    
                    {/* Admin routes */}
                    <Route path="/admin" element={
                        <ProtectedRoute adminOnly>
                            <MainLayout><AdminPage /></MainLayout>
                        </ProtectedRoute>
                    } />
                </Routes>
                <Toaster position="top-right" richColors />
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
