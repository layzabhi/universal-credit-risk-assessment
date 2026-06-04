import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

import { useState, useEffect } from "react";
import axios from "axios";

import {
  ShieldCheck,
  Activity,
  AlertTriangle
} from "lucide-react";

import { motion } from "framer-motion";

function App() {

  const [formData, setFormData] = useState({

    // PERSONAL

    fullName: "",
    age: "",
    gender: "",

    maritalStatus: "",
    dependents: "",

    // EMPLOYMENT

    employmentType: "",
    monthsEmployed: "",

    monthlyIncome: "",

    // FINANCIAL

    creditScore: "",

    existingDebt: "",

    // LOAN

    loanAmount: "",
    loanPurpose: "",

    loanTerm: "",

    // ADDITIONAL

    homeOwnership: "",

    coSigner: "No"
  });

  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);

  const [predictionHistory, setPredictionHistory] = useState([]);

  const riskDistributionData = [

  {
    name: "Defaulters",
    value: predictionHistory.filter(
      p => p.prediction === "Defaulter"
    ).length
  },

  {
    name: "Non-Defaulters",
    value: predictionHistory.filter(
      p => p.prediction === "Non-Defaulter"
    ).length
  }
];

const confidenceData = predictionHistory
  .slice(0, 6)
  .reverse()
  .map((item, index) => ({

    name: `P${index + 1}`,

    confidence: Number(item.confidence)
  }));

const COLORS = [
  "#ef4444",
  "#22c55e"
];

  // LOAD HISTORY ONCE

  useEffect(() => {

    const savedHistory = localStorage.getItem(
      "predictionHistory"
    );

    if (savedHistory) {

      setPredictionHistory(
        JSON.parse(savedHistory)
      );
    }

  }, []);

  // SAVE HISTORY

  useEffect(() => {

    if (predictionHistory.length > 0) {

      localStorage.setItem(
        "predictionHistory",
        JSON.stringify(predictionHistory)
      );
    }

  }, [predictionHistory]);

  const handleChange = (e) => {

    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePredict = async () => {

    try {

      setLoading(true);

      const annualIncome =
        Number(formData.monthlyIncome || 0) * 12;

      const creditScore =
        Number(formData.creditScore || 650);

      const extSource =
        Math.min(
          Math.max(
            creditScore / 850,
            0
          ),
          1
        );

      const loanAmount =
        Number(formData.loanAmount || 0);

      const payload = {

        AMT_INCOME_TOTAL:
          annualIncome,

        AMT_CREDIT:
          loanAmount,

        AMT_ANNUITY:
          loanAmount / 12,

        AMT_GOODS_PRICE:
          loanAmount,

        DAYS_BIRTH:
          -Number(formData.age || 30) * 365,

        DAYS_EMPLOYED:
          -Number(formData.monthsEmployed || 12) * 30,

        CNT_FAM_MEMBERS:
          Number(formData.dependents || 1),

        EXT_SOURCE_1:
          extSource,

        EXT_SOURCE_2:
          extSource,

        EXT_SOURCE_3:
          extSource
      };

      const response = await axios.post(
        "http://127.0.0.1:8000/predict",
        payload
      );

      setResult(response.data);

      const newPrediction = {

        ...response.data,

        timestamp: new Date().toLocaleTimeString(),

        confidence: (
          Math.max(
            response.data.default_probability,
            1 - response.data.default_probability
          ) * 100
        ).toFixed(1)
      };

      setPredictionHistory(prev => [
        newPrediction,
        ...prev
      ]);

    } catch (error) {

      console.error(
        "Prediction Error:",
        error.response?.data || error
      );

      alert("Prediction failed");

    } finally {

      setLoading(false);
    }
  };

  return (

    <div className="min-h-screen bg-slate-950 text-white">

      {/* NAVBAR */}

      <nav className="border-b border-slate-800 backdrop-blur-lg">

        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

          <div className="flex items-center gap-3">

            <div className="bg-cyan-500 p-2 rounded-xl">
              <ShieldCheck size={22} />
            </div>

            <h1 className="text-2xl font-bold tracking-wide">
              CreditAI
            </h1>

          </div>

          <div className="flex gap-6 text-slate-300">

            <button className="hover:text-cyan-400 transition">
              Dashboard
            </button>

            <button className="hover:text-cyan-400 transition">
              Analytics
            </button>

            <button className="hover:text-cyan-400 transition">
              Risk Engine
            </button>

          </div>

        </div>

      </nav>

      {/* MAIN SECTION */}

      <section className="max-w-7xl mx-auto px-6 py-16">

        <div className="grid lg:grid-cols-2 gap-10 items-start">

          {/* LEFT */}

          <div>

            <div className="inline-flex items-center gap-2 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full text-cyan-400 mb-6">

              <Activity size={18} />

              Enterprise AI Credit Intelligence

            </div>

            <h1 className="text-6xl font-bold leading-tight">

              Real-Time
              <span className="text-cyan-400">
                {" "}Credit Risk{" "}
              </span>

              Assessment Platform

            </h1>

            <p className="text-slate-400 mt-6 text-lg leading-relaxed">

              Advanced AI-powered fintech system for intelligent
              defaulter prediction, explainable underwriting,
              and enterprise-grade credit analytics.

            </p>

          </div>

          {/* RIGHT CARD */}

          <div className="bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl">

            <div className="flex items-center justify-between mb-8">

              <h2 className="text-2xl font-semibold">
                Risk Assessment
              </h2>

              <AlertTriangle
                className="text-yellow-400"
                size={28}
              />

            </div>

            <div className="space-y-8">

              {/* PERSONAL PROFILE */}

              <div>

                <div className="flex items-center justify-between mb-6">

                  <div>

                    <h3 className="text-xl font-semibold text-cyan-400">

                      Personal Profile

                    </h3>

                    <p className="text-slate-400 text-sm mt-1">

                      Applicant demographic information

                    </p>

                  </div>

                  <div className="bg-cyan-500/10 text-cyan-400 px-3 py-1 rounded-full text-xs font-semibold">

                    REQUIRED

                  </div>

                </div>

                <div className="grid grid-cols-2 gap-4">

                  {/* FULL NAME */}

                  <div className="col-span-2">

                    <label className="text-sm text-slate-400 mb-2 block">

                      Full Name

                    </label>

                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      placeholder="Enter applicant full name"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                  {/* AGE */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Age

                    </label>

                    <input
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      placeholder="Applicant age"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                  {/* GENDER */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Gender

                    </label>

                    <select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    >

                      <option value="">
                        Select Gender
                      </option>

                      <option value="Male">
                        Male
                      </option>

                      <option value="Female">
                        Female
                      </option>

                    </select>

                  </div>

                  {/* MARITAL STATUS */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Marital Status

                    </label>

                    <select
                      name="maritalStatus"
                      value={formData.maritalStatus}
                      onChange={handleChange}
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    >

                      <option value="">
                        Select Status
                      </option>

                      <option value="Single">
                        Single
                      </option>

                      <option value="Married">
                        Married
                      </option>

                      <option value="Divorced">
                        Divorced
                      </option>

                    </select>

                  </div>

                  {/* DEPENDENTS */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Dependents

                    </label>

                    <input
                      type="number"
                      name="dependents"
                      value={formData.dependents}
                      onChange={handleChange}
                      placeholder="Number of dependents"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                </div>

              </div>

              {/* FINANCIAL PROFILE */}

              <div>

                <div className="flex items-center justify-between mb-6">

                  <div>

                    <h3 className="text-xl font-semibold text-cyan-400">

                      Financial Profile

                    </h3>

                    <p className="text-slate-400 text-sm mt-1">

                      Creditworthiness and debt analysis

                    </p>

                  </div>

                  <div className="bg-yellow-500/10 text-yellow-400 px-3 py-1 rounded-full text-xs font-semibold">

                    RISK ANALYSIS

                  </div>

                </div>

                <div className="grid grid-cols-2 gap-4">

                  {/* LOAN DETAILS */}

                  <div>

                    <div className="flex items-center justify-between mb-6">

                      <div>

                        <h3 className="text-xl font-semibold text-cyan-400">

                          Loan Details

                        </h3>

                        <p className="text-slate-400 text-sm mt-1">

                          Requested loan structure and underwriting scenario

                        </p>

                      </div>

                      <div className="bg-purple-500/10 text-purple-400 px-3 py-1 rounded-full text-xs font-semibold">

                        UNDERWRITING
                      </div>

                    </div>

                    <div className="grid grid-cols-2 gap-4">

                      {/* LOAN AMOUNT */}

                      <div>

                        <label className="text-sm text-slate-400 mb-2 block">

                          Loan Amount

                        </label>

                        <input
                          type="number"
                          name="loanAmount"
                          value={formData.loanAmount}
                          onChange={handleChange}
                          placeholder="Requested loan amount"
                          className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                        />

                      </div>

                      {/* LOAN TERM */}

                      <div>

                        <label className="text-sm text-slate-400 mb-2 block">

                          Loan Term (Months)

                        </label>

                        <input
                          type="number"
                          name="loanTerm"
                          value={formData.loanTerm}
                          onChange={handleChange}
                          placeholder="Loan repayment duration"
                          className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                        />

                      </div>

                      {/* LOAN PURPOSE */}

                      <div className="col-span-2">

                        <label className="text-sm text-slate-400 mb-2 block">

                          Loan Purpose

                        </label>

                        <select
                          name="loanPurpose"
                          value={formData.loanPurpose}
                          onChange={handleChange}
                          className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                        >

                          <option value="">
                            Select Loan Purpose
                          </option>

                          <option value="Personal">
                            Personal Loan
                          </option>

                          <option value="Business">
                            Business Expansion
                          </option>

                          <option value="Education">
                            Education
                          </option>

                          <option value="Vehicle">
                            Vehicle Purchase
                          </option>

                          <option value="Home">
                            Home Financing
                          </option>

                          <option value="Medical">
                            Medical Emergency
                          </option>

                        </select>

                      </div>

                    </div>

                  </div>

                  {/* EXISTING DEBT */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Existing Debt

                    </label>

                    <input
                      type="number"
                      name="existingDebt"
                      value={formData.existingDebt}
                      onChange={handleChange}
                      placeholder="Current liabilities"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                  {/* HOME OWNERSHIP */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Home Ownership

                    </label>

                    <select
                      name="homeOwnership"
                      value={formData.homeOwnership}
                      onChange={handleChange}
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    >

                      <option value="">
                        Select Ownership
                      </option>

                      <option value="Owned">
                        Owned
                      </option>

                      <option value="Mortgaged">
                        Mortgaged
                      </option>

                      <option value="Rented">
                        Rented
                      </option>

                    </select>

                  </div>

                  {/* CO-SIGNER */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Co-Signer Support

                    </label>

                    <select
                      name="coSigner"
                      value={formData.coSigner}
                      onChange={handleChange}
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    >

                      <option value="No">
                        No Co-Signer
                      </option>

                      <option value="Yes">
                        Has Co-Signer
                      </option>

                    </select>

                  </div>

                </div>

              </div>

              {/* EMPLOYMENT PROFILE */}

              <div>

                <div className="flex items-center justify-between mb-6">

                  <div>

                    <h3 className="text-xl font-semibold text-cyan-400">

                      Employment Profile

                    </h3>

                    <p className="text-slate-400 text-sm mt-1">

                      Employment stability and income assessment

                    </p>

                  </div>

                  <div className="bg-green-500/10 text-green-400 px-3 py-1 rounded-full text-xs font-semibold">

                    VERIFIED

                  </div>

                </div>

                <div className="grid grid-cols-2 gap-4">

                  {/* EMPLOYMENT TYPE */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Employment Type

                    </label>

                    <select
                      name="employmentType"
                      value={formData.employmentType}
                      onChange={handleChange}
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    >

                      <option value="">
                        Select Employment
                      </option>

                      <option value="Salaried">
                        Salaried
                      </option>

                      <option value="Self-Employed">
                        Self-Employed
                      </option>

                      <option value="Business">
                        Business Owner
                      </option>

                      <option value="Freelancer">
                        Freelancer
                      </option>

                    </select>

                  </div>

                  {/* MONTHS EMPLOYED */}

                  <div>

                    <label className="text-sm text-slate-400 mb-2 block">

                      Employment Duration (Months)

                    </label>

                    <input
                      type="number"
                      name="monthsEmployed"
                      value={formData.monthsEmployed}
                      onChange={handleChange}
                      placeholder="Employment duration"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                  {/* MONTHLY INCOME */}

                  <div className="col-span-2">

                    <label className="text-sm text-slate-400 mb-2 block">

                      Monthly Income

                    </label>

                    <input
                      type="number"
                      name="monthlyIncome"
                      value={formData.monthlyIncome}
                      onChange={handleChange}
                      placeholder="Enter verified monthly income"
                      className="w-full bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 outline-none focus:border-cyan-400 transition"
                    />

                  </div>

                </div>

              </div>

              {/* CREDIT SCORES */}

              <div>

                <h3 className="text-lg font-semibold mb-4 text-cyan-400">
                  Credit Intelligence
                </h3>

                <div className="grid grid-cols-3 gap-4">

                  <input
                    type="number"
                    step="0.01"
                    name="ext1"
                    value={formData.ext1}
                    onChange={handleChange}
                    placeholder="EXT 1"
                    className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-cyan-400"
                  />

                  <input
                    type="number"
                    step="0.01"
                    name="ext2"
                    value={formData.ext2}
                    onChange={handleChange}
                    placeholder="EXT 2"
                    className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-cyan-400"
                  />

                  <input
                    type="number"
                    step="0.01"
                    name="ext3"
                    value={formData.ext3}
                    onChange={handleChange}
                    placeholder="EXT 3"
                    className="bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-cyan-400"
                  />

                </div>

              </div>

              {/* BUTTON */}

              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full bg-cyan-500 hover:bg-cyan-400 transition text-black font-bold py-4 rounded-2xl shadow-lg shadow-cyan-500/20"
              >

                {
                  loading
                    ? "Analyzing..."
                    : "Predict Risk"
                }

              </button>

              {/* RESULT */}

              {
                result && (

                  <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="mt-8"
                  >

                    <div className="bg-slate-950 border border-slate-700 rounded-3xl p-6">

                      <div className="flex items-center justify-between mb-6">

                        <h3 className="text-2xl font-semibold">
                          AI Risk Analysis
                        </h3>

                        <div className={`
                          px-4 py-2 rounded-full text-sm font-bold
                          ${
                            result.default_probability < 0.25
                              ? "bg-green-500/20 text-green-400"
                              : result.default_probability < 0.50
                              ? "bg-yellow-500/20 text-yellow-400"
                              : "bg-red-500/20 text-red-400"
                          }
                        `}>

                          {
                            result.default_probability < 0.25
                              ? "LOW RISK"
                              : result.default_probability < 0.50
                              ? "MEDIUM RISK"
                              : "HIGH RISK"
                          }

                        </div>

                      </div>

                      <div className="mb-8">

                        <div className="flex justify-between mb-2">

                          <span className="text-slate-400">
                            Default Probability
                          </span>

                          <span className="font-bold text-cyan-400">

                            {
                              (
                                result.default_probability * 100
                              ).toFixed(2)
                            }%

                          </span>

                        </div>

                        <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden">

                          <motion.div
                            initial={{ width: 0 }}
                            animate={{
                              width: `${result.default_probability * 100}%`
                            }}
                            transition={{ duration: 1 }}
                            className={`
                              h-4 rounded-full
                              ${
                                result.default_probability < 0.25
                                  ? "bg-green-400"
                                  : result.default_probability < 0.50
                                  ? "bg-yellow-400"
                                  : "bg-red-500"
                              }
                            `}
                          />

                        </div>

                      </div>

                      <div className="grid grid-cols-2 gap-4">

                        <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800">

                          <p className="text-slate-400 text-sm">
                            Prediction
                          </p>

                          <h4 className={`
                            text-xl font-bold mt-2
                            ${
                              result.prediction === "Defaulter"
                                ? "text-red-400"
                                : "text-green-400"
                            }
                          `}>

                            {result.prediction}

                          </h4>

                        </div>

                        <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800">

                          <p className="text-slate-400 text-sm">
                            AI Confidence
                          </p>

                          <h4 className="text-xl font-bold mt-2 text-cyan-400">

                            {
                              (
                                Math.max(
                                  result.default_probability,
                                  1 - result.default_probability
                                ) * 100
                              ).toFixed(1)
                            }%

                          </h4>

                        </div>

                      </div>

                      {/* AI EXPLAINABILITY */}

                      <div className="mt-8 grid lg:grid-cols-2 gap-6">

                        {/* RISK INCREASERS */}

                        <div className="bg-red-500/5 border border-red-500/20 rounded-3xl p-6">

                          <div className="flex items-center justify-between mb-6">

                            <h3 className="text-xl font-semibold text-red-400">

                              Risk Increasers

                            </h3>

                            <div className="text-sm text-red-300">
                              Negative Signals
                            </div>

                          </div>

                          <div className="space-y-4">

                            {
                              result.risk_increasers?.length > 0

                                ? result.risk_increasers.map(
                                    (item, index) => (

                                      <div
                                        key={index}
                                        className="bg-slate-900/80 border border-red-500/10 rounded-2xl p-4"
                                      >

                                        <div className="flex items-center justify-between mb-3">

                                          <h4 className="font-semibold text-white">

                                            {item.feature}

                                          </h4>

                                          <span className={`
                                            px-3 py-1 rounded-full text-xs font-bold
                                            ${
                                              item.impact === "High"
                                                ? "bg-red-500/20 text-red-400"
                                                : "bg-yellow-500/20 text-yellow-400"
                                            }
                                          `}>

                                            {item.impact}

                                          </span>

                                        </div>

                                        <p className="text-slate-400 text-sm leading-relaxed">

                                          {item.reason}

                                        </p>

                                      </div>
                                    )
                                  )

                                : (

                                  <div className="text-slate-400 text-sm">
                                    No major risk increasers detected.
                                  </div>
                                )
                            }

                          </div>

                        </div>

                        {/* RISK REDUCERS */}

                        <div className="bg-green-500/5 border border-green-500/20 rounded-3xl p-6">

                          <div className="flex items-center justify-between mb-6">

                            <h3 className="text-xl font-semibold text-green-400">

                              Risk Reducers

                            </h3>

                            <div className="text-sm text-green-300">
                              Positive Signals
                            </div>

                          </div>

                          <div className="space-y-4">

                            {
                              result.risk_reducers?.length > 0

                                ? result.risk_reducers.map(
                                    (item, index) => (

                                      <div
                                        key={index}
                                        className="bg-slate-900/80 border border-green-500/10 rounded-2xl p-4"
                                      >

                                        <div className="flex items-center justify-between mb-3">

                                          <h4 className="font-semibold text-white">

                                            {item.feature}

                                          </h4>

                                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-500/20 text-green-400">

                                            {item.impact}

                                          </span>

                                        </div>

                                        <p className="text-slate-400 text-sm leading-relaxed">

                                          {item.reason}

                                        </p>

                                      </div>
                                    )
                                  )

                                : (

                                  <div className="text-slate-400 text-sm">
                                    No major positive indicators detected.
                                  </div>
                                )
                            }

                          </div>

                        </div>

                      </div>

                    </div>

                  </motion.div>
                )
              }

            </div>

          </div>

        </div>

      </section>

      {/* ANALYTICS */}

      <div className="max-w-7xl mx-auto px-6 pb-20">

        <div className="flex items-center justify-between mb-8">

          <h2 className="text-3xl font-bold">
            AI Analytics Dashboard
          </h2>

          <div className="text-slate-400">
            Live Underwriting Intelligence
          </div>

        </div>

        <div className="grid lg:grid-cols-4 gap-6 mb-10">

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <p className="text-slate-400 text-sm">
              Total Predictions
            </p>

            <h3 className="text-4xl font-bold mt-4 text-cyan-400">

              {predictionHistory.length}

            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <p className="text-slate-400 text-sm">
              Defaulters
            </p>

            <h3 className="text-4xl font-bold mt-4 text-red-400">

              {
                predictionHistory.filter(
                  p => p.prediction === "Defaulter"
                ).length
              }

            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <p className="text-slate-400 text-sm">
              Non-Defaulters
            </p>

            <h3 className="text-4xl font-bold mt-4 text-green-400">

              {
                predictionHistory.filter(
                  p => p.prediction === "Non-Defaulter"
                ).length
              }

            </h3>

          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <p className="text-slate-400 text-sm">
              Avg Confidence
            </p>

            <h3 className="text-4xl font-bold mt-4 text-yellow-400">

              {
                predictionHistory.length > 0

                  ? (
                    predictionHistory.reduce(
                      (acc, curr) =>
                        acc + Number(curr.confidence),
                      0
                    ) / predictionHistory.length
                  ).toFixed(1)

                  : 0
              }%

            </h3>

          </div>

        </div>

        {/* CHARTS */}

        <div className="grid lg:grid-cols-2 gap-8 mb-10">

          {/* PIE CHART */}

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <div className="flex items-center justify-between mb-6">

              <h3 className="text-2xl font-semibold">
                Risk Distribution
              </h3>

              <div className="text-slate-400">
                Portfolio Overview
              </div>

            </div>

            <div className="h-[320px]">

              <ResponsiveContainer width="100%" height="100%">

                <PieChart>

                  <Pie
                    data={riskDistributionData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    dataKey="value"
                    label
                  >

                    {
                      riskDistributionData.map(
                        (entry, index) => (

                          <Cell
                            key={index}
                            fill={COLORS[index % COLORS.length]}
                          />
                        )
                      )
                    }

                  </Pie>

                  <Tooltip />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>

          {/* BAR CHART */}

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">

            <div className="flex items-center justify-between mb-6">

              <h3 className="text-2xl font-semibold">
                AI Confidence Trend
              </h3>

              <div className="text-slate-400">
                Recent Predictions
              </div>

            </div>

            <div className="h-[320px]">

              <ResponsiveContainer width="100%" height="100%">

                <BarChart
                  data={confidenceData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#334155"
                  />

                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                  />

                  <YAxis
                    stroke="#94a3b8"
                  />

                  <Tooltip />

                  <Bar
                    dataKey="confidence"
                    fill="#06b6d4"
                    radius={[8, 8, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default App;