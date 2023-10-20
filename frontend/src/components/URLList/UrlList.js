import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API = "http://127.0.0.1:8000/api/urls";

const InputComponent = () => {
  const [keywords, setKeywords] = useState({
    raw_filename: "",
    url: "",
    type: "",
    folder_name: "",
  });
  const [editingIndex, setEditingIndex] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const data = location.state && location.state.data;
    console.log(data);
    if (data) {
      setKeywords(data);
      setEditingIndex(data.id);
    }
  }, [location.state]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setKeywords((prevKeywords) => ({
      ...prevKeywords,
      [name]: name === "type" && !value ? "pdf" : value,
    }));
  };

  const handleSubmit = () => {
    if (editingIndex !== null) {
      fetch(`${API}/${editingIndex}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(keywords),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Data updated successfully:", data);
        })
        .catch((error) => {
          console.error("Error updating data:", error);
        });
    } else {
      fetch(API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(keywords),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Data sent successfully:", data);
        })
        .catch((error) => {
          console.error("Error sending data:", error);
        });
    }
  };

  const handleAddMoreSection = () => {
    setKeywords({
      raw_filename: "",
      url: "",
      type: "",
      folder_name: "",
    });
    setEditingIndex(null);
  };

  return (
    <div className="d-flex flex-column align-items-center">
      <div className="card w-50">
        <h5 className="card-header">POC for Invesco</h5>
        <div className="card-body p-2">
          <h5 className="card-title">This is for url listing</h5>
          <section>
          <div className="row mb-3">
            <div className="col-md-6">
              <label className="form-label">File Name</label>
              <input
                type="text"
                className="form-control"
                name="raw_filename"
                value={keywords.raw_filename}
                onChange={handleInputChange}
                disabled={editingIndex !== null}
              />
            </div>
            <div className="col-md-6">
              <label className="form-label">Enter URL</label>
              <input
                type="text"
                className="form-control"
                name="url"
                value={keywords.url}
                onChange={handleInputChange}
              />
            </div>
            <div className="col-md-6 mt-3">
              <label className="form-label">Type</label>
              <select
                className="form-select"
                name="type"
                value={keywords.type}
                onChange={handleInputChange}
                disabled={editingIndex !== null}
              >
                <option value="">Select Type</option>
                <option value="pdf">PDF</option>
                <option value="link">Link</option>
                <option value="html">HTML</option>
              </select>
            </div>
            <div className="col-md-6 mt-3">
              <label className="form-label">Folder Name</label>
              <input
                type="text"
                className="form-control"
                name="folder_name"
                value={keywords.folder_name}
                onChange={handleInputChange}
                disabled={editingIndex !== null}
              />
            </div>
          </div>
          </section>
          <div className=" d-flex justify-content-between">
            {editingIndex === null && (
              <button
                className="btn btn-secondary"
                onClick={handleAddMoreSection}
              >
                Add More
              </button>
            )}
            <button className="btn btn-primary" onClick={handleSubmit}>
              Submit
            </button>
          </div>
        </div>
      </div>
      <br />
      <button
        className="btn btn-primary "
        onClick={() => navigate("/lookuptable")}
      >
        Go to Lookup Table page
      </button>
      <br />
      <button
        className="btn btn-primary"
        onClick={() => navigate("/")}
      >
        Goto Detail Page
      </button>
    </div>
  );
};

export default InputComponent;
