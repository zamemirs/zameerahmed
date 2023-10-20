import React, { useState } from "react";

const API = "http://127.0.0.1:8000/api/webscraping/"; 

export default function WebScrapping() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [filePath, setFilePath] = useState("");
  
  const startJob = async () => {
    try {
      setLoading(true);
      const response = await fetch(API, {
        method: "POST", 
      });
      const data = await response.json(); 

      if (response.status === 200 && data.status === "success") {
        setStatus("Success");
        setFilePath(data.file_link); 
      } else {
        setStatus("Failed");
      }
    } catch (error) {
      setStatus("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex justify-content-center">
      <div className="card w-50 h-50">
        <div className="card text-center">
          <div className="card-header">Web Scraping Job</div>
          <div className="card-body">
            <h2 className="card-title">Web Scraping Job</h2>
            <p className="card-text">Get started with web scraping</p>
            {loading ? (
              <div>
                <div
                  className="spinner-grow text-primary"
                  role="status"
                  style={{ width: "100px", height: "100px" }}
                ></div>
              </div>
            ) : (
              <button className="btn btn-primary" onClick={startJob}>
                Start Job
              </button>
            )}
          </div>

          {status === "Success" ? (
            <div>
              <button type="button" className="btn btn-outline-success" disabled>
                Success
              </button>{" "}
              
              {filePath && <p>Click to download: <a href={filePath} download="data.csv" onClick={startJob}>
                Start Job and Download CSV
              </a></p>}
            </div>
          ) : status === "Failed" ? (
            <div>Job Failed. Please try again later.</div>
          ) : (
            <></>
          )}
        </div>
      </div>
    </div>
  );
}