import {
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  Legend
} from "recharts";

import { useState, useEffect } from "react";
import axios from "axios";
import {
  ShieldCheck,
  Activity,
  AlertTriangle,
  FileText,
  UploadCloud,
  Settings,
  Database,
  Lock,
  LogOut,
  UserCheck,
  TrendingUp,
  Sliders,
  TrendingDown,
  RefreshCw,
  Info,
  Users,
  Plus
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const BACKEND_URL = "http://127.0.0.1:8000";

function App() {
  // Authentication State
  const [token, setToken] = useState(localStorage.getItem("auth_token") || "");
  const [username, setUsername] = useState(localStorage.getItem("auth_username") || "Guest");
  const [role, setRole] = useState(localStorage.getItem("auth_role") || "Guest");
  
  // Modals & Panels UI
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [authError, setAuthError] = useState("");
  const [loading, setLoading] = useState(false);

  // UI Tabs & Views
  const [activeTab, setActiveTab] = useState("single");

  // Single Predict View State
  const [formData, setFormData] = useState({
    fullName: "",
    age: "35",
    income: "65000",
    loanAmount: "15000",
    employmentYears: "5",
    dependents: "0",
    creditScore: "",
    loanGrade: "B",
    loanIntRate: "12.5",
    creditHistory: "existing paid",
    defaultHistory: "0"
  });
  
  const [singleResult, setSingleResult] = useState(null);
  const [simulationMode, setSimulationMode] = useState(false);

  // Batch Portfolio View State
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [portfolioHistory, setPortfolioHistory] = useState([]);
  const [uploadStatus, setUploadStatus] = useState("");

  // Governance State
  const [governanceLogs, setGovernanceLogs] = useState([]);

  // Admin Panel State
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminTotalUsers, setAdminTotalUsers] = useState(0);
  const [adminRegisterData, setAdminRegisterData] = useState({ username: "", password: "", role: "Risk Analyst" });
  const [adminError, setAdminError] = useState("");
  const [adminSuccess, setAdminSuccess] = useState("");

  // Axios instance with JWT authorization
  const api = axios.create({
    baseURL: BACKEND_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });

  // Load Portfolio History & Governance Logs on tab change if logged in
  useEffect(() => {
    if (token) {
      if (activeTab === "single" || activeTab === "batch") {
        fetchPortfolioHistory();
      }
      if (activeTab === "governance") {
        fetchGovernanceLogs();
      }
      if (activeTab === "admin" && role === "Admin") {
        fetchAdminUsers();
      }
    }
  }, [token, activeTab]);

  const fetchPortfolioHistory = async () => {
    try {
      const response = await api.get("/api/portfolio/history");
      setPortfolioHistory(response.data);
    } catch (err) {
      console.error("Failed to fetch portfolio history", err);
    }
  };

  const fetchGovernanceLogs = async () => {
    try {
      const response = await api.get("/api/governance");
      setGovernanceLogs(response.data);
    } catch (err) {
      console.error("Failed to fetch governance logs", err);
    }
  };

  const fetchAdminUsers = async () => {
    try {
      const response = await api.get("/api/admin/users");
      setAdminUsers(response.data.users);
      setAdminTotalUsers(response.data.total_users);
    } catch (err) {
      console.error("Failed to fetch user logs", err);
    }
  };

  // Auth Handlers
  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError("");
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("username", loginData.username);
      params.append("password", loginData.password);
      
      const response = await axios.post(`${BACKEND_URL}/api/auth/login`, params);
      const { access_token, role, username } = response.data;
      
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("auth_username", username);
      localStorage.setItem("auth_role", role);
      
      setToken(access_token);
      setUsername(username);
      setRole(role);
      
      setIsLoginModalOpen(false);
      setLoginData({ username: "", password: "" });
      
      // Redirect Admin to admin tab, others stay
      if (role === "Admin") {
        setActiveTab("admin");
      }
    } catch (err) {
      setAuthError(err.response?.data?.detail || "Login failed. Check credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_username");
    localStorage.removeItem("auth_role");
    setToken("");
    setUsername("Guest");
    setRole("Guest");
    setSingleResult(null);
    setPortfolioResults(null);
    setActiveTab("single");
  };

  // Admin New User Registration
  const handleAdminRegister = async (e) => {
    e.preventDefault();
    setAdminError("");
    setAdminSuccess("");
    try {
      const response = await api.post("/api/auth/register", adminRegisterData);
      setAdminSuccess(`User "${adminRegisterData.username}" registered successfully!`);
      setAdminRegisterData({ username: "", password: "", role: "Risk Analyst" });
      fetchAdminUsers();
    } catch (err) {
      setAdminError(err.response?.data?.detail || "Registration failed.");
    }
  };

  // Single Predict Handlers
  const handleFormChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePredict = async () => {
    if (!token) {
      setIsLoginModalOpen(true);
      return;
    }
    if (!formData.fullName) {
      alert("Please enter the applicant's name");
      return;
    }
    setLoading(true);
    try {
      const payload = {
        full_name: formData.fullName,
        income: parseFloat(formData.income || 0),
        age: parseFloat(formData.age || 0),
        loan_amount: parseFloat(formData.loanAmount || 0),
        employment_years: parseFloat(formData.employmentYears || 0),
        dependents: parseInt(formData.dependents || 0),
        credit_score: formData.creditScore ? parseFloat(formData.creditScore) : null,
        loan_grade: formData.loanGrade || null,
        loan_int_rate: formData.loanIntRate ? parseFloat(formData.loanIntRate) : null,
        credit_history: formData.creditHistory || null,
        default_history: formData.defaultHistory ? parseFloat(formData.defaultHistory) : null
      };

      const response = await api.post("/api/predict", payload);
      setSingleResult(response.data);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (applicantId, fullName) => {
    try {
      const response = await api.get(`/api/applicants/${applicantId}/report`, {
        responseType: 'blob'
      });
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);
      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', `Underwriting_Report_${fullName.replace(" ", "_")}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to export PDF report.");
    }
  };

  // What-If Simulator Adjustments
  const simulateAdjustment = (type) => {
    setSimulationMode(true);
    if (type === "income") {
      setFormData(prev => ({ ...prev, income: (parseFloat(prev.income) + 15000).toString() }));
    } else if (type === "loan") {
      setFormData(prev => ({ ...prev, loanAmount: Math.max(2000, parseFloat(prev.loanAmount) - 5000).toString() }));
    } else if (type === "score") {
      setFormData(prev => ({ ...prev, creditScore: Math.min(850, parseFloat(prev.creditScore || 600) + 70).toString() }));
    } else if (type === "history") {
      setFormData(prev => ({ ...prev, creditHistory: "good", defaultHistory: "0" }));
    }
  };

  const resetSimulation = () => {
    setSimulationMode(false);
    setFormData(prev => ({
      ...prev,
      income: "65000",
      loanAmount: "15000",
      creditScore: "",
      creditHistory: "existing paid",
      defaultHistory: "0"
    }));
  };

  // Batch Portfolio Handlers
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadStatus("Uploading & Analyzing CSV...");
    const uploadFormData = new FormData();
    uploadFormData.append("file", file);

    try {
      const response = await api.post("/api/portfolio/predict", uploadFormData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setPortfolioResults(response.data);
      setUploadStatus("Analysis Completed Successfully!");
      fetchPortfolioHistory();
    } catch (err) {
      console.error(err);
      setUploadStatus("");
      alert(err.response?.data?.detail || "CSV Upload & Prediction failed.");
    }
  };

  const handleDownloadRejectedCSV = () => {
    if (!portfolioResults || !portfolioResults.results) return;
    
    // Filter for rejected applicants (where prediction is "Defaulter")
    const rejected = portfolioResults.results.filter(
      (r) => r.prediction === "Defaulter"
    );
    
    if (rejected.length === 0) {
      alert("No rejected applicants found in this portfolio run!");
      return;
    }
    
    // Extract headers: all keys of the first row
    const headers = Object.keys(rejected[0]);
    
    // Build CSV content
    const csvRows = [];
    csvRows.push(headers.join(",")); // Header row
    
    for (const row of rejected) {
      const values = headers.map(header => {
        const val = row[header];
        if (val === null || val === undefined) {
          return "";
        }
        const stringVal = String(val);
        if (stringVal.includes(",") || stringVal.includes("\"") || stringVal.includes("\n")) {
          return `"${stringVal.replace(/"/g, '""')}"`;
        }
        return stringVal;
      });
      csvRows.push(values.join(","));
    }
    
    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    const safeFilename = (portfolioResults.filename || "portfolio").replace(".csv", "");
    link.setAttribute("download", `${safeFilename}_rejected_applicants.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const COLORS = ["#06b6d4", "#eab308", "#ef4444"]; // cyan, yellow, red

  // Render Risk Distributions for batch portfolio
  const getRiskDistributionData = () => {
    if (!portfolioResults) return [];
    const dist = portfolioResults.risk_distribution;
    return [
      { name: "Low Risk", value: dist.low_risk },
      { name: "Medium Risk", value: dist.medium_risk },
      { name: "High Risk", value: dist.high_risk }
    ];
  };

  const getConfidenceData = () => {
    if (!portfolioResults || !portfolioResults.results) return [];
    return portfolioResults.results.slice(0, 15).map((r, i) => {
      const prob = r.default_probability;
      const confidence = prob > 0.5 ? prob : (1 - prob);
      return {
        name: `App ${i+1}`,
        confidence: Math.round(confidence * 100)
      };
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col font-sans">
      {/* GLOW BACKGROUND EFFECT */}
      <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-[radial-gradient(circle,rgba(6,182,212,0.05),transparent_70%)] pointer-events-none" />
      <div className="absolute bottom-0 left-10 w-[500px] h-[500px] bg-[radial-gradient(circle,rgba(139,92,246,0.05),transparent_70%)] pointer-events-none" />

      {/* NAVBAR */}
      <nav className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-cyan-500 p-2 rounded-xl shadow-lg shadow-cyan-500/20">
              <ShieldCheck size={22} className="text-black" />
            </div>
            <h1 className="text-2xl font-bold tracking-wide">
              Credit<span className="text-cyan-400">Risk</span> Enterprise
            </h1>
          </div>

          <div className="flex gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("single")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer ${activeTab === "single" ? "bg-cyan-500 text-black shadow" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}
            >
              Single Predictor
            </button>
            <button
              onClick={() => setActiveTab("batch")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer ${activeTab === "batch" ? "bg-cyan-500 text-black shadow" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}
            >
              Batch Portfolio
            </button>
            {token && (
              <button
                onClick={() => setActiveTab("governance")}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer ${activeTab === "governance" ? "bg-cyan-500 text-black shadow" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}
              >
                Governance Registry
              </button>
            )}
            {token && role === "Admin" && (
              <button
                onClick={() => setActiveTab("admin")}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer ${activeTab === "admin" ? "bg-cyan-500 text-black shadow" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}
              >
                Admin Panel
              </button>
            )}
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
              <UserCheck size={14} className="text-cyan-400" />
              <span className="font-semibold text-slate-300">{username}</span>
              <span className="text-slate-500">|</span>
              <span className="bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded text-[10px] font-bold uppercase">{role}</span>
            </div>
            
            {token ? (
              <button
                onClick={handleLogout}
                className="text-slate-400 hover:text-red-400 p-2 rounded-xl hover:bg-slate-900 transition cursor-pointer"
                title="Sign Out"
              >
                <LogOut size={20} />
              </button>
            ) : (
              <button
                onClick={() => setIsLoginModalOpen(true)}
                className="bg-cyan-500 hover:bg-cyan-400 transition text-black font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 cursor-pointer"
              >
                <Lock size={14} /> Sign In
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* MAIN CONTAINER */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full z-10">
        
        {/* SINGLE PREDICTOR TAB */}
        {activeTab === "single" && (
          <div className="grid lg:grid-cols-2 gap-8 items-start">
            {/* LEFT INPUT FORM */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-slate-900/40 backdrop-blur-md border border-slate-800 rounded-3xl p-6 shadow-xl"
            >
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-xl font-bold">Risk Assessment Profiler</h2>
                  <p className="text-xs text-slate-400 mt-1">Assess individual credit application and calculate risk scores</p>
                </div>
                {!token && (
                  <span className="bg-slate-800 text-slate-400 px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                    Read-Only Guest
                  </span>
                )}
              </div>

              <div className="space-y-6">
                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Applicant Full Name</label>
                  <input
                    type="text"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleFormChange}
                    placeholder="Enter full name"
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">Age (Years)</label>
                    <input
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleFormChange}
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">Dependents Count</label>
                    <input
                      type="number"
                      name="dependents"
                      value={formData.dependents}
                      onChange={handleFormChange}
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">Annual Income ($)</label>
                    <input
                      type="number"
                      name="income"
                      value={formData.income}
                      onChange={handleFormChange}
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">Loan Requested ($)</label>
                    <input
                      type="number"
                      name="loanAmount"
                      value={formData.loanAmount}
                      onChange={handleFormChange}
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">Employment tenure (Years)</label>
                    <input
                      type="number"
                      name="employmentYears"
                      value={formData.employmentYears}
                      onChange={handleFormChange}
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-2 font-medium">FICO Credit Score (Optional)</label>
                    <input
                      type="number"
                      name="creditScore"
                      value={formData.creditScore}
                      onChange={handleFormChange}
                      placeholder="e.g. 300 - 850 (leave empty for SCQS)"
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />
                  </div>
                </div>

                <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 space-y-4">
                  <h3 className="text-xs font-bold text-cyan-400 tracking-wider uppercase">Risk Signals (Optional Engine Overrides)</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[10px] text-slate-500 block mb-1.5 uppercase font-medium">Loan Grade</label>
                      <select
                        name="loanGrade"
                        value={formData.loanGrade}
                        onChange={handleFormChange}
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm outline-none focus:border-cyan-400 transition"
                      >
                        <option value="A">Grade A (Lowest risk)</option>
                        <option value="B">Grade B</option>
                        <option value="C">Grade C</option>
                        <option value="D">Grade D</option>
                        <option value="E">Grade E</option>
                        <option value="F">Grade F</option>
                        <option value="G">Grade G (Highest risk)</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-[10px] text-slate-500 block mb-1.5 uppercase font-medium">Interest Rate (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        name="loanIntRate"
                        value={formData.loanIntRate}
                        onChange={handleFormChange}
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm outline-none focus:border-cyan-400 transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[10px] text-slate-500 block mb-1.5 uppercase font-medium">Credit Status History</label>
                      <select
                        name="creditHistory"
                        value={formData.creditHistory}
                        onChange={handleFormChange}
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm outline-none focus:border-cyan-400 transition"
                      >
                        <option value="existing paid">Existing Credits Paid (Good)</option>
                        <option value="critical">Critical Account / Other Credits (Risk)</option>
                        <option value="delayed">Delay in paying in past (Risk)</option>
                        <option value="all paid">No credit history (Clean)</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-[10px] text-slate-500 block mb-1.5 uppercase font-medium">Delinquency Count</label>
                      <input
                        type="number"
                        name="defaultHistory"
                        value={formData.defaultHistory}
                        onChange={handleFormChange}
                        className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm outline-none focus:border-cyan-400 transition"
                      />
                    </div>
                  </div>
                </div>

                {!token && (
                  <div className="bg-slate-950/80 border border-slate-800 text-slate-400 px-4 py-3 rounded-2xl text-xs flex items-center gap-2">
                    <Info size={16} className="text-cyan-400 flex-shrink-0" />
                    <span>You are browsing in Read-Only Guest Mode. <button onClick={() => setIsLoginModalOpen(true)} className="text-cyan-400 font-bold hover:underline bg-transparent border-0 cursor-pointer">Sign In</button> to evaluate applicant risk.</span>
                  </div>
                )}

                <button
                  onClick={handlePredict}
                  disabled={loading || !token}
                  className="w-full bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed transition text-black font-bold py-4 rounded-2xl shadow-lg shadow-cyan-500/20 flex justify-center items-center gap-2 cursor-pointer"
                >
                  {loading ? "Analyzing risk profile..." : "Evaluate Credit Decision"}
                </button>
              </div>
            </motion.div>

            {/* RIGHT DECISION OUTPUT PANEL */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              {singleResult ? (
                <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
                  {/* HEADER */}
                  <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                    <div>
                      <h2 className="text-xl font-bold">AI Decision Panel</h2>
                      <p className="text-xs text-slate-400 mt-1">Reflects risk calculations in real-time</p>
                    </div>
                    <button
                      onClick={() => handleDownloadPDF(singleResult.id, singleResult.full_name)}
                      className="bg-slate-800 border border-slate-700 hover:bg-slate-700 hover:border-cyan-400/50 text-cyan-400 px-3 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer"
                    >
                      <FileText size={14} /> Download PDF Report
                    </button>
                  </div>

                  {/* PROBABILITY GAUGE AND RATING */}
                  <div className="grid md:grid-cols-2 gap-6 items-center">
                    <div className="relative w-44 h-44 mx-auto flex items-center justify-center">
                      <div className={`absolute inset-0 rounded-full blur-3xl opacity-10 ${singleResult.risk_level === "LOW" ? "bg-emerald-500" : (singleResult.risk_level === "MEDIUM" ? "bg-yellow-500" : "bg-red-500")}`} />
                      
                      <svg className="w-44 h-44 -rotate-90" viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="82" stroke="#1e293b" strokeWidth="12" fill="none" />
                        <circle
                          cx="100" cy="100" r="82"
                          stroke={singleResult.risk_level === "LOW" ? "#10b981" : (singleResult.risk_level === "MEDIUM" ? "#eab308" : "#ef4444")}
                          strokeWidth="12" fill="none"
                          strokeDasharray={515}
                          strokeDashoffset={515 - (singleResult.default_probability * 515)}
                          strokeWidth="12"
                          strokeLinecap="round"
                          className="transition-all duration-1000"
                        />
                      </svg>
                      
                      <div className="absolute text-center">
                        <div className="text-4xl font-extrabold">{Math.round(singleResult.default_probability * 100)}%</div>
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Default risk</div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
                        <div className="text-xs text-slate-500 font-medium">Underwriting Recommendation</div>
                        <div className={`text-2xl font-black mt-1 ${singleResult.prediction === "Non-Defaulter" ? "text-emerald-400" : "text-red-400"}`}>
                          {singleResult.prediction === "Non-Defaulter" ? "APPROVED" : "REJECTED"}
                        </div>
                      </div>
                      
                      <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
                        <div className="text-xs text-slate-500 font-medium">Risk Exposure Rating</div>
                        <div className={`text-lg font-bold mt-1 ${singleResult.risk_level === "LOW" ? "text-emerald-400" : (singleResult.risk_level === "MEDIUM" ? "text-yellow-400" : "text-red-400")}`}>
                          {singleResult.risk_level} RISK
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* SHAP WATERFALL CHART */}
                  <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xs font-bold text-cyan-400 tracking-wider uppercase">Explainable AI: Key Risk Drivers (SHAP)</h3>
                      <span className="text-[10px] text-slate-500">Log-odds influence</span>
                    </div>

                    <div className="h-60">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          layout="vertical"
                          data={singleResult.explanation?.contributions?.slice(0, 5) || []}
                          margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                          <XAxis type="number" stroke="#64748b" />
                          <YAxis 
                            dataKey="feature" 
                            type="category" 
                            stroke="#64748b" 
                            tickFormatter={(tick) => tick.replace("_", " ").toUpperCase()} 
                            width={100}
                            style={{ fontSize: '9px', fontWeight: '600' }}
                          />
                          <RechartsTooltip 
                            contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", color: "#fff" }}
                            formatter={(value) => [`${value.toFixed(4)}`, 'Risk Impact']}
                          />
                          <Bar dataKey="shap_value" radius={[4, 4, 4, 4]}>
                            {
                              (singleResult.explanation?.contributions || []).slice(0, 5).map((entry, index) => (
                                <Cell 
                                  key={`cell-${index}`} 
                                  fill={entry.shap_value > 0 ? "#ef4444" : "#10b981"} 
                                />
                              ))
                            }
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* WHAT-IF SIMULATION MODULE */}
                  <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xs font-bold text-cyan-400 tracking-wider uppercase">What-If Decision Simulator</h3>
                        <p className="text-[10px] text-slate-500 mt-0.5">Modify parameters dynamically to check if risk output clears threshold</p>
                      </div>
                      <Sliders size={18} className="text-cyan-400" />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => simulateAdjustment("income")}
                        className="bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/20 transition rounded-xl p-2.5 text-left text-xs cursor-pointer"
                      >
                        <div className="text-emerald-400 font-semibold flex items-center gap-1">
                          <TrendingUp size={12} /> Increase Income
                        </div>
                        <div className="text-[9px] text-slate-500 mt-1">Simulate $15k income increase</div>
                      </button>

                      <button
                        onClick={() => simulateAdjustment("loan")}
                        className="bg-cyan-500/10 border border-cyan-500/20 hover:bg-cyan-500/20 transition rounded-xl p-2.5 text-left text-xs cursor-pointer"
                      >
                        <div className="text-cyan-400 font-semibold flex items-center gap-1">
                          <TrendingDown size={12} /> Lower Loan Amount
                        </div>
                        <div className="text-[9px] text-slate-500 mt-1">Deduct $5k from request</div>
                      </button>

                      <button
                        onClick={() => simulateAdjustment("score")}
                        className="bg-yellow-500/10 border border-yellow-500/20 hover:bg-yellow-500/20 transition rounded-xl p-2.5 text-left text-xs cursor-pointer"
                      >
                        <div className="text-yellow-400 font-semibold flex items-center gap-1">
                          <TrendingUp size={12} /> Optimize Credit Score
                        </div>
                        <div className="text-[9px] text-slate-500 mt-1">Add +70 points override</div>
                      </button>

                      <button
                        onClick={() => simulateAdjustment("history")}
                        className="bg-violet-500/10 border border-violet-500/20 hover:bg-violet-500/20 transition rounded-xl p-2.5 text-left text-xs cursor-pointer"
                      >
                        <div className="text-violet-400 font-semibold flex items-center gap-1">
                          <ShieldCheck size={12} /> Perfect History
                        </div>
                        <div className="text-[9px] text-slate-500 mt-1">Zero out defaults & set good history</div>
                      </button>
                    </div>

                    {simulationMode && (
                      <div className="flex items-center justify-between bg-violet-500/10 border border-violet-500/20 rounded-xl p-3 text-xs">
                        <div className="text-violet-400 flex items-center gap-2">
                          <RefreshCw size={14} className="animate-spin" />
                          <span>Simulation parameters active</span>
                        </div>
                        <div className="flex gap-2">
                          <button 
                            onClick={handlePredict}
                            className="bg-cyan-500 hover:bg-cyan-400 text-black px-2.5 py-1 rounded font-bold cursor-pointer"
                          >
                            Re-Run Predict
                          </button>
                          <button 
                            onClick={resetSimulation}
                            className="bg-slate-800 hover:bg-slate-700 text-white px-2.5 py-1 rounded cursor-pointer"
                          >
                            Reset
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-slate-900/20 border border-slate-800/80 border-dashed rounded-3xl p-12 text-center text-slate-500 h-full flex flex-col items-center justify-center">
                  <Activity size={48} className="text-slate-700 mb-4 animate-pulse" />
                  <h3 className="text-lg font-bold text-slate-400">Waiting for Assessment</h3>
                  <p className="text-xs text-slate-500 max-w-xs mt-2 mx-auto">Fill in the applicant profile details on the left and trigger prediction to generate credit decisions.</p>
                </div>
              )}
            </motion.div>
          </div>
        )}

        {/* BATCH PORTFOLIO TAB */}
        {activeTab === "batch" && (
          <div className="space-y-8">
            <div className="grid md:grid-cols-3 gap-6">
              {/* UPLOAD PANEL */}
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl col-span-1"
              >
                <div className="flex items-center gap-2 text-cyan-400 font-bold mb-4">
                  <UploadCloud size={20} />
                  <h3>Upload Portfolio File</h3>
                </div>
                
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Upload applicant CSV datasets. The recognition engine automatically identifies the schema (German, Home Credit, LendingClub, or Give Me Some Credit) and normalizes the attributes.
                </p>

                <div className="relative border border-slate-800 border-dashed hover:border-cyan-400/50 bg-slate-950/50 rounded-2xl p-6 text-center transition">
                  {token ? (
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileUpload}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                  ) : null}
                  <UploadCloud size={32} className={`mx-auto mb-2 ${token ? "text-cyan-400" : "text-slate-700"}`} />
                  {token ? (
                    <>
                      <span className="text-xs block text-slate-300 font-medium">Click to select CSV file</span>
                      <span className="text-[10px] block text-slate-500 mt-1">or drag and drop here</span>
                    </>
                  ) : (
                    <>
                      <span className="text-xs block text-slate-400 font-semibold">Upload Disabled (Read-Only)</span>
                      <span className="text-[10px] block text-slate-600 mt-1">
                        <button onClick={() => setIsLoginModalOpen(true)} className="text-cyan-400 hover:underline bg-transparent border-0 cursor-pointer font-bold">Sign In</button> to upload portfolio runs
                      </span>
                    </>
                  )}
                </div>

                {uploadStatus && (
                  <div className="mt-4 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs py-2 px-3 rounded-lg text-center font-medium animate-pulse">
                    {uploadStatus}
                  </div>
                )}
              </motion.div>

              {/* KPI DASHBOARD CARDS */}
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="col-span-2 grid grid-cols-2 gap-4"
              >
                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Dataset Type Recognized</span>
                    <h3 className="text-2xl font-black text-cyan-400 mt-2">
                      {portfolioResults ? portfolioResults.dataset_type : "No File Loaded"}
                    </h3>
                  </div>
                  <div className="text-[10px] text-slate-500 flex items-center gap-1.5 mt-4">
                    <Info size={12} />
                    <span>Mapping transformation applied successfully</span>
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Total Applicants Processed</span>
                    <h3 className="text-4xl font-black text-white mt-2">
                      {portfolioResults ? portfolioResults.total_applicants : "0"}
                    </h3>
                  </div>
                  <span className="text-[10px] text-slate-500">Stored inside persistent DB registries</span>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Avg Portfolio Risk Score</span>
                    <h3 className="text-4xl font-black text-yellow-400 mt-2">
                      {portfolioResults ? `${Math.round(portfolioResults.average_risk * 100)}%` : "0%"}
                    </h3>
                  </div>
                  <span className="text-[10px] text-slate-500">Aggregate default risk average</span>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">Approved / Rejected Counts</span>
                    <h3 className="text-2xl font-black text-white mt-2">
                      {portfolioResults ? (
                        <><span className="text-emerald-400">{(portfolioResults.total_applicants - portfolioResults.rejected)}</span> / <span className="text-red-400">{portfolioResults.rejected}</span></>
                      ) : "0 / 0"}
                    </h3>
                  </div>
                  <span className="text-[10px] text-slate-500">Based on model calibration threshold</span>
                </div>
              </motion.div>
            </div>

            {/* VISUALIZATION ENGINE CHARTS */}
            {portfolioResults && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid md:grid-cols-2 gap-6"
              >
                {/* RISK DISTRIBUTION PIE */}
                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Risk Distribution Segmentation</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getRiskDistributionData()}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {getRiskDistributionData().map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", color: "#fff" }}
                        />
                        <Legend verticalAlign="bottom" height={36} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* CONFIDENCE TREND CHART */}
                <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl">
                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">AI Confidence Distribution Profile</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={getConfidenceData()}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: '10px' }} />
                        <YAxis stroke="#64748b" style={{ fontSize: '10px' }} />
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b", color: "#fff" }}
                          formatter={(value) => [`${value}%`, 'Confidence Rating']}
                        />
                        <Line type="monotone" dataKey="confidence" stroke="#8b5cf6" strokeWidth={3} dot={{ fill: '#8b5cf6', strokeWidth: 2 }} activeDot={{ r: 8 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </motion.div>
            )}

            {/* RESULTS LIST TABLE */}
            {portfolioResults && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl"
              >
                <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
                  <div>
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Processed Applicant Records (First 50 rows)</h3>
                    <p className="text-[10px] text-slate-500 mt-1">Showing top results from this portfolio run</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={handleDownloadRejectedCSV}
                      className="bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 text-red-400 px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer shadow-lg shadow-red-500/5"
                    >
                      <AlertTriangle size={14} /> Download Rejected (CSV)
                    </button>
                    <span className="bg-cyan-500/10 text-cyan-400 px-3 py-2 rounded-full text-xs font-bold">PERSISTED IN DATABASE</span>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                        <th className="py-3 px-4 font-semibold">Applicant Identifier</th>
                        <th className="py-3 px-4 font-semibold">Normalized Age</th>
                        <th className="py-3 px-4 font-semibold">Annual Income</th>
                        <th className="py-3 px-4 font-semibold">Loan Requested</th>
                        <th className="py-3 px-4 font-semibold">FICO Score</th>
                        <th className="py-3 px-4 font-semibold">Risk Probability</th>
                        <th className="py-3 px-4 font-semibold">AI Decision</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {portfolioResults.results.slice(0, 50).map((row, index) => {
                        const prob = row.default_probability;
                        return (
                          <tr key={index} className="hover:bg-slate-900/50 transition">
                            <td className="py-3.5 px-4 font-bold text-slate-200">
                              {row.name || row.full_name || `Applicant ${index+1}`}
                            </td>
                            <td className="py-3.5 px-4 text-slate-400">
                              {row.age ? Math.round(row.age) : "N/A"}
                            </td>
                            <td className="py-3.5 px-4 text-slate-400">
                              {row.income ? `$${Math.round(row.income).toLocaleString()}` : "N/A"}
                            </td>
                            <td className="py-3.5 px-4 text-slate-400">
                              {row.loan_amount ? `$${Math.round(row.loan_amount).toLocaleString()}` : "N/A"}
                            </td>
                            <td className="py-3.5 px-4 text-slate-300 font-semibold">
                              {row.credit_score ? Math.round(row.credit_score) : "N/A"}
                            </td>
                            <td className="py-3.5 px-4 font-bold text-slate-300">
                              {Math.round(prob * 100)}%
                            </td>
                            <td className="py-3.5 px-4">
                              <span className={`px-2.5 py-1 rounded-full font-bold text-[9px] uppercase border ${row.prediction === "Non-Defaulter" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" : "bg-red-500/10 border-red-500/20 text-red-400"}`}>
                                {row.prediction === "Non-Defaulter" ? "Approve" : "Reject"}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {/* PORTFOLIO RUNS HISTORY LIST */}
            {token && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl"
              >
                <div className="flex items-center gap-2 text-slate-400 font-bold mb-6">
                  <Database size={18} />
                  <h3>Portfolio Batch Audit Run Logs</h3>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                        <th className="py-3 px-4 font-semibold">Batch Filename</th>
                        <th className="py-3 px-4 font-semibold">Dataset Category</th>
                        <th className="py-3 px-4 font-semibold">Total Records</th>
                        <th className="py-3 px-4 font-semibold">Approval Rate</th>
                        <th className="py-3 px-4 font-semibold">Average Risk</th>
                        <th className="py-3 px-4 font-semibold">High Risk Count</th>
                        <th className="py-3 px-4 font-semibold">Execution Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {portfolioHistory.map((run) => (
                        <tr key={run.id} className="hover:bg-slate-900/50 transition">
                          <td className="py-3 px-4 font-semibold text-cyan-400">{run.filename}</td>
                          <td className="py-3 px-4 text-slate-400">{run.dataset_type}</td>
                          <td className="py-3 px-4 text-slate-300 font-medium">{run.total_applicants}</td>
                          <td className="py-3 px-4 text-emerald-400 font-semibold">{Math.round(run.approval_rate * 100)}%</td>
                          <td className="py-3 px-4 text-yellow-400 font-semibold">{Math.round(run.average_risk * 100)}%</td>
                          <td className="py-3 px-4 text-red-400 font-semibold">{run.high_risk_count}</td>
                          <td className="py-3 px-4 text-slate-500">{run.created_at}</td>
                        </tr>
                      ))}
                      {portfolioHistory.length === 0 && (
                        <tr>
                          <td colSpan={7} className="py-8 text-center text-slate-600">No batch runs logged in database yet.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </div>
        )}

        {/* MODEL GOVERNANCE REGISTRY TAB */}
        {activeTab === "governance" && token && (
          <div className="space-y-8">
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl"
            >
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
                <div className="bg-cyan-500/10 p-2.5 rounded-2xl text-cyan-400">
                  <ShieldCheck size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold">Model Governance Registry</h2>
                  <p className="text-xs text-slate-400 mt-1">Audit log of model version metadata, performance logs, and calibrated decision thresholds</p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                      <th className="py-3 px-4 font-semibold">Model Version</th>
                      <th className="py-3 px-4 font-semibold">Validation ROC-AUC</th>
                      <th className="py-3 px-4 font-semibold">F1 Optimization</th>
                      <th className="py-3 px-4 font-semibold">Calibrated Threshold</th>
                      <th className="py-3 px-4 font-semibold">Features Used Count</th>
                      <th className="py-3 px-4 font-semibold">Deploy Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {governanceLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-900/50 transition">
                        <td className="py-4 px-4 font-bold text-cyan-400">{log.version}</td>
                        <td className="py-4 px-4 text-emerald-400 font-extrabold">{log.roc_auc.toFixed(4)}</td>
                        <td className="py-4 px-4 text-emerald-400 font-bold">{log.f1.toFixed(4)}</td>
                        <td className="py-4 px-4 text-yellow-400 font-extrabold">{log.threshold.toFixed(2)}</td>
                        <td className="py-4 px-4 text-slate-300">{log.features_used.split(",").length} Features</td>
                        <td className="py-4 px-4 text-slate-500">{log.training_date}</td>
                      </tr>
                    ))}
                    {governanceLogs.length === 0 && (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-slate-600">No model governance registries logged yet.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>

            {/* PERFORMANCE PARAMETERS PANEL */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* TARGET MATRIX INFORMATION */}
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4"
              >
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-800">Platform Feature Metrics</h3>
                
                <div className="space-y-4 text-xs">
                  <div className="flex justify-between items-center bg-slate-950/50 p-3.5 rounded-2xl border border-slate-800/50">
                    <span className="text-slate-400">Target Metrics (ROC-AUC)</span>
                    <span className="font-bold text-emerald-400">&gt; 0.80 Target (Achieved 0.8603)</span>
                  </div>
                  
                  <div className="flex justify-between items-center bg-slate-950/50 p-3.5 rounded-2xl border border-slate-800/50">
                    <span className="text-slate-400">Target Metrics (F1-score)</span>
                    <span className="font-bold text-emerald-400">&gt; 0.40 Target (Achieved 0.6380)</span>
                  </div>

                  <div className="flex justify-between items-center bg-slate-950/50 p-3.5 rounded-2xl border border-slate-800/50">
                    <span className="text-slate-400">Ensemble Components</span>
                    <span className="text-slate-300">LightGBM, XGBoost, CatBoost</span>
                  </div>

                  <div className="flex justify-between items-center bg-slate-950/50 p-3.5 rounded-2xl border border-slate-800/50">
                    <span className="text-slate-400">Probability Calibration Method</span>
                    <span className="text-slate-300">CalibratedClassifierCV (Sigmoid/Platt Scaling)</span>
                  </div>
                </div>
              </motion.div>

              {/* REGISTERED FEATURES LIST */}
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl"
              >
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-800 mb-4">Unified Schema Input Parameters</h3>
                
                <div className="flex flex-wrap gap-2">
                  {governanceLogs.length > 0 && governanceLogs[0].features_used.split(",").map((feature, i) => (
                    <span key={i} className="bg-slate-950 border border-slate-800 text-slate-400 px-3 py-1.5 rounded-xl text-xs font-semibold hover:border-cyan-500/20 transition">
                      {feature.trim().replace("_", " ").toUpperCase()}
                    </span>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        )}

        {/* ADMIN PANEL TAB */}
        {activeTab === "admin" && token && role === "Admin" && (
          <div className="grid lg:grid-cols-3 gap-8 items-start">
            {/* REGISTERED USERS LIST */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl lg:col-span-2 space-y-6"
            >
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Users className="text-cyan-400" size={20} />
                  <h2 className="text-lg font-bold">Registered Users Accounts</h2>
                </div>
                <span className="bg-cyan-500/10 text-cyan-400 px-2.5 py-1 rounded-full text-xs font-bold">
                  {adminTotalUsers} ACTIVE USERS
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                      <th className="py-3 px-4 font-semibold">User Reference ID</th>
                      <th className="py-3 px-4 font-semibold">Username</th>
                      <th className="py-3 px-4 font-semibold">Access Role</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {adminUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-900/50 transition">
                        <td className="py-3.5 px-4 text-slate-500 font-mono">#{user.id}</td>
                        <td className="py-3.5 px-4 font-bold text-slate-200">{user.username}</td>
                        <td className="py-3.5 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${user.role === "Admin" ? "bg-cyan-500/10 text-cyan-400" : "bg-violet-500/10 text-violet-400"}`}>
                            {user.role}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>

            {/* ADD USER FORM */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6"
            >
              <div className="pb-4 border-b border-slate-800">
                <h2 className="text-lg font-bold">Add System Account</h2>
                <p className="text-xs text-slate-400 mt-1">Register new credentials and assign specific permission roles</p>
              </div>

              {adminError && (
                <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3 rounded-xl text-center">
                  {adminError}
                </div>
              )}
              {adminSuccess && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs p-3 rounded-xl text-center">
                  {adminSuccess}
                </div>
              )}

              <form onSubmit={handleAdminRegister} className="space-y-4">
                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Username</label>
                  <input
                    type="text"
                    required
                    placeholder="Enter username"
                    value={adminRegisterData.username}
                    onChange={(e) => setAdminRegisterData({ ...adminRegisterData, username: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs outline-none focus:border-cyan-400 transition"
                  />
                </div>
                
                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Temporary Password</label>
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={adminRegisterData.password}
                    onChange={(e) => setAdminRegisterData({ ...adminRegisterData, password: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs outline-none focus:border-cyan-400 transition"
                  />
                </div>

                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Assigned Role</label>
                  <select
                    value={adminRegisterData.role}
                    onChange={(e) => setAdminRegisterData({ ...adminRegisterData, role: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs outline-none focus:border-cyan-400 transition text-slate-300"
                  >
                    <option value="Risk Analyst">Risk Analyst</option>
                    <option value="Admin">Admin</option>
                  </select>
                </div>

                <button
                  type="submit"
                  className="w-full bg-cyan-500 hover:bg-cyan-400 transition text-black font-bold py-3.5 rounded-2xl shadow-lg shadow-cyan-500/20 flex justify-center items-center gap-1.5 text-xs cursor-pointer"
                >
                  <Plus size={14} /> Create Account
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </main>

      {/* LOGIN MODAL OVERLAY */}
      <AnimatePresence>
        {isLoginModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => { setIsLoginModalOpen(false); setAuthError(""); }}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative z-10 text-white"
            >
              <div className="flex flex-col items-center mb-6">
                <div className="bg-cyan-500 p-2.5 rounded-2xl mb-3 shadow-lg shadow-cyan-500/20">
                  <ShieldCheck size={26} className="text-black" />
                </div>
                <h1 className="text-2xl font-extrabold tracking-tight">
                  Credit<span className="text-cyan-400">Risk</span> System Sign-In
                </h1>
                <p className="text-slate-400 text-xs mt-1 text-center">
                  Enter credentials to unlock write and evaluation privileges
                </p>
              </div>

              {authError && (
                <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs px-4 py-2.5 rounded-xl mb-4 text-center">
                  {authError}
                </div>
              )}

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Username</label>
                  <input
                    type="text"
                    required
                    placeholder="admin or analyst"
                    value={loginData.username}
                    onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs outline-none focus:border-cyan-400 transition"
                  />
                </div>
                
                <div>
                  <label className="text-xs text-slate-400 block mb-2 font-medium">Password</label>
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs outline-none focus:border-cyan-400 transition"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-cyan-500 hover:bg-cyan-400 transition text-black font-bold py-3.5 rounded-2xl shadow-lg shadow-cyan-500/20 flex justify-center items-center gap-1.5 text-xs cursor-pointer"
                  >
                    {loading ? "Authenticating..." : <><Lock size={14} /> Sign In</>}
                  </button>
                </div>
              </form>

              <button
                onClick={() => { setIsLoginModalOpen(false); setAuthError(""); }}
                className="w-full bg-transparent border border-slate-800 hover:border-slate-700 transition text-slate-400 hover:text-slate-300 py-3 rounded-2xl text-xs mt-3 cursor-pointer"
              >
                Cancel & Browse as Guest
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* FOOTER */}
      <footer className="border-t border-slate-900 bg-slate-950/50 py-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-cyan-400" />
            <span>Credit Risk AI Underwriting System. Licensed for enterprise use.</span>
          </div>
          <div>
            <span>System Version 2.0.0 (Universal Model) • SQLite/PostgreSQL Dynamic Layer</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;