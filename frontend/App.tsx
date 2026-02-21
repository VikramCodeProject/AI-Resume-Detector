/**
 * Resume Truth Verification System - Frontend
 * React.js 18+ with TypeScript & Material UI v5
 */

import React, { useState, useEffect } from "react";
import {
  Container,
  Box,
  Paper,
  Button,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";

import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
} from "@mui/icons-material";

import axios from "axios";

// ===================== API BASE =====================
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ===================== TYPES =====================

interface Claim {
  id: string;
  claim_type: "skill" | "education" | "experience" | "certification" | "project";
  claim_text: string;
  confidence: number;
}

interface MLPrediction {
  claim_id: string;
  prediction: "verified" | "doubtful" | "fake";
  confidence: number;
  shap_explanation?: string;
}

interface ResumeData {
  resume_id: string;
  filename: string;
  status: "uploaded" | "processing" | "completed" | "failed";
  uploaded_at: string;
  trust_score?: {
    overall_score: number;
    verified_count: number;
    doubtful_count: number;
    fake_count: number;
    generated_at: string;
  };
  claims?: Claim[];
  predictions?: MLPrediction[];
  blockchain_hash?: string;
}

interface UploadResponse {
  resume_id: string;
  status: string;
  message: string;
  processing_job_id: string;
}

// ===================== TRUST SCORE GAUGE =====================

const TrustScoreGauge: React.FC<{ score: number }> = ({ score }) => {
  const getColor = (score: number) => {
    if (score >= 80) return "#4caf50";
    if (score >= 60) return "#ff9800";
    return "#f44336";
  };

  const getLabel = (score: number) => {
    if (score >= 80) return "Verified";
    if (score >= 60) return "Doubtful";
    return "Fake";
  };

  return (
    <Box sx={{ textAlign: "center", py: 3 }}>
      <Box sx={{ position: "relative", display: "inline-flex" }}>
        <CircularProgress
          variant="determinate"
          value={score}
          size={200}
          thickness={4}
          sx={{ color: getColor(score) }}
        />

        <Box
          sx={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
          }}
        >
          <Typography variant="h3" fontWeight="bold">
            {score.toFixed(1)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {getLabel(score)}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

// ===================== UPLOAD COMPONENT =====================

const ResumeUploadComponent: React.FC<{ onUploadSuccess: (id: string) => void }> = ({
  onUploadSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const MAX_SIZE = 5 * 1024 * 1024; // 5MB

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (
      ![
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ].includes(selected.type)
    ) {
      setError("Only PDF and DOCX files allowed");
      return;
    }

    if (selected.size > MAX_SIZE) {
      setError("File size must be less than 5MB");
      return;
    }

    setFile(selected);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post<UploadResponse>(
        `${API}/api/resumes/upload`,
        formData
      );

      onUploadSuccess(res.data.resume_id);
      setFile(null);
    } catch {
      setError("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5">Upload Resume</Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Box
        sx={{
          border: "2px dashed #ccc",
          p: 3,
          textAlign: "center",
          mt: 2,
          cursor: "pointer",
        }}
      >
        <input hidden type="file" id="file" onChange={handleFileChange} />
        <label htmlFor="file">
          <CloudUploadIcon sx={{ fontSize: 50, color: "#1976d2" }} />
          <Typography>{file ? file.name : "Click to upload PDF/DOCX"}</Typography>
        </label>
      </Box>

      <Button
        variant="contained"
        fullWidth
        sx={{ mt: 2 }}
        disabled={!file || uploading}
        onClick={handleUpload}
      >
        {uploading ? <CircularProgress size={20} /> : "Upload & Verify"}
      </Button>
    </Paper>
  );
};

// ===================== RESULTS COMPONENT =====================

const VerificationResultsComponent: React.FC<{ data: ResumeData }> = ({ data }) => {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<MLPrediction | null>(null);

  const chipColor = (
    p: string
  ): "success" | "warning" | "error" | "default" => {
    if (p === "verified") return "success";
    if (p === "doubtful") return "warning";
    if (p === "fake") return "error";
    return "default";
  };

  return (
    <>
      {/* Trust Score */}
      {data.trust_score && (
        <Paper sx={{ p: 3, mb: 2 }}>
          <Typography variant="h5">Trust Score</Typography>
          <TrustScoreGauge score={data.trust_score.overall_score} />
        </Paper>
      )}

      {/* Claims Table */}
      {data.predictions && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h5">Claims Analysis</Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Claim</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Prediction</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {data.predictions.map((p) => (
                  <TableRow key={p.claim_id}>
                    <TableCell>
                      {data.claims?.find((c) => c.id === p.claim_id)?.claim_text}
                    </TableCell>
                    <TableCell>
                      {data.claims?.find((c) => c.id === p.claim_id)?.claim_type}
                    </TableCell>
                    <TableCell>
                      <Chip label={p.prediction} color={chipColor(p.prediction)} />
                    </TableCell>
                    <TableCell>{(p.confidence * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      <Button
                        onClick={() => {
                          setSelected(p);
                          setOpen(true);
                        }}
                      >
                        Explain
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Explanation Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>AI Explanation</DialogTitle>
        <DialogContent>
          <Typography>{selected?.shap_explanation}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

// ===================== MAIN APP =====================

const App: React.FC = () => {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [data, setData] = useState<ResumeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Polling Effect
  useEffect(() => {
    if (!resumeId) return;
    let timer: NodeJS.Timeout;

    const poll = async () => {
      setLoading(true);
      try {
        const res = await axios.get<ResumeData>(`${API}/api/resumes/${resumeId}`);
        setData(res.data);

        if (res.data.status === "processing") {
          timer = setTimeout(poll, 3000);
        }
      } catch {
        setError("Fetch failed");
      } finally {
        setLoading(false);
      }
    };

    poll();
    return () => clearTimeout(timer);
  }, [resumeId]);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" textAlign="center" fontWeight="bold">
        Resume Truth Verification System
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <ResumeUploadComponent onUploadSuccess={setResumeId} />
        </Grid>

        <Grid item xs={12} md={8}>
          {!data && <Paper sx={{ p: 3 }}>Upload resume to start</Paper>}
          {data && <VerificationResultsComponent data={data} />}

          {data?.blockchain_hash && (
            <Alert severity="success">
              Blockchain Hash: {data.blockchain_hash}
            </Alert>
          )}

          {data && (
            <Button fullWidth variant="outlined" startIcon={<DownloadIcon />}>
              Download Report
            </Button>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default App;
