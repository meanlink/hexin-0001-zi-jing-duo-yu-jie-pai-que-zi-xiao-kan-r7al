import { api, identity, pollJob } from "../ui.js";

const proofPath = code => "/proofs/" + encodeURIComponent(code);
const post = body => ({method: "POST", body});

export const glyphApi = {
  proofs: () => api("/proofs"),
  faces: () => api("/typefaces"),
  addProof: form => api("/proofs", post(form)),
  addFace: form => api("/typefaces", post(form)),
  review: code => api(proofPath(code) + "/review"),
  revise: (code, form) => api(proofPath(code), {method: "PATCH", body: form}),
  rank: async (code, revision) => {
    const job = await api(proofPath(code) + "/proposals", post({revision}));
    return pollJob(job.job_id);
  },
  assign: (code, form) => api(proofPath(code) + "/assignments", {method: "PUT", body: form}),
  lock: (code, revision) => api(proofPath(code) + "/lock", post({revision})),
  manifest: code => api(proofPath(code) + "/manifest"),
  benchmark: () => api("/benchmarks/latest"),
  measure: async () => {
    const job = await api("/benchmarks", {method: "POST"});
    return pollJob(job.job_id);
  },
};

export async function downloadManifest(code, revision) {
  const response = await fetch("/api" + proofPath(code) + "/manifest.csv", {
    headers: {Authorization: "Bearer " + identity().token}
  });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail ?? "暂时无法下载");
  }
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = code + "-r" + revision + ".csv";
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
