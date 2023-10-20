import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

//const URL_API = "http://56e3-210-212-195-98.ngrok-free.app/api/urls/";

 const URL_API = 'http://127.0.0.1:8000/api/urls/'

export default function UrlTable() {
  const [urlList, setUrlList] = useState([]);
 
  const navigate = useNavigate();


  const getResponce = async () => {
    try {
        const response = await fetch(URL_API);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const jsRes = await response.json();
        setUrlList(jsRes)
    } catch (error) {
        console.error('Error:', error);
    }
};

  useEffect(() => {
    getResponce();
  }, []);

  const handleEditClick = (id, data) => {
    console.log(id, data)
    navigate(`/urlList/${id}`, { state: { data } });
  };

  const handleDeleteClick = async (id) => {
    try {
      await fetch(`${URL_API}/${id}`, {
        method: "DELETE",
      });
      setUrlList(urlList.filter((item) => item.id !== id));
    } catch (error) {
      console.error("Error deleting item:", error);
    }
  };
  return (
    <div>
      <div>
        <div>
          <div className="">
            <table className="table">
              <thead>
                <tr>
                  <th scope="col" style={{ width: "10%" }}>id</th>
                  <th scope="col" style={{ width: "10%" }}>File Name</th>
                  <th scope="col" style={{width:'40%'}}>URL </th>
                  <th scope="col" style={{ width: "10%" }}>Type</th>
                  <th scope="col" style={{ width: "10%" }}>Folder Name</th>
                  <th scope="col" style={{ width: "20%" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                
                {urlList.map((list) => (
                  
                  <tr key={list.id}>
                    <th scope="row">{list.id}</th>
                    <td className="text-wrap">{list.raw_filename}</td>
                    <td className="text-wrap">{list.url}</td>
                    <td className="text-wrap">{list.type}</td>
                    <td className="text-wrap">{list.folder_name}</td>
                    <td className="text-wrap">
                      <button
                        className="btn btn-outline-primary"
                        onClick={() => handleEditClick(list.id, list)}
                      >
                        Edit
                      </button>{" "}
                      <button
                        className="btn btn-outline-danger"
                        onClick={() => handleDeleteClick(list.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
