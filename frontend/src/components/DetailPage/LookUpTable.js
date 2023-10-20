import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

//const LOOKUP_API = "http://56e3-210-212-195-98.ngrok-free.app/api/lookup-keyword/";
 
 const LOOKUP_API = 'http://127.0.0.1:8000/api/lookup-keyword/'

export default function LookUp() {
  const [lookupList, setLookUpList] = useState([]);  
  const navigate = useNavigate();

  const getResponce = async () => {
    const responce = await fetch(LOOKUP_API);
    const jsRes = await responce.json();
    console.log(jsRes)
    setLookUpList(jsRes)
  };

  useEffect(() => {
    getResponce();
  }, []);

  const handleEditClick = (id, data) => {
    console.log(id, data)
    navigate(`/lookuptable/${id}`, { state:  [data]  });
  };
  

  const handleDeleteClick = async (id) => {
    try {
      await fetch(`${LOOKUP_API}${id}`, {
        method: "DELETE",
      });
      setLookUpList(lookupList.filter((item) => item.id !== id));
    } catch (error) {
      console.error("Error deleting item:", error);
    }
  };

  return (
    <div>
      <div>
        <div className="">
          <table className="table">
            <thead>
              <tr>
                <th scope="col" style={{ width: "10%" }}>
                  id
                </th>
                <th scope="col" style={{ width: "10%" }}>
                  Keyword
                </th>
                <th scope="col" style={{ width: "70%" }}>
                  list
                </th>
                <th scope="col" style={{ width: "10%" }}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {lookupList.map((list) => (
                <tr key={list.id}>
                  <th scope="row">{list.id}</th>
                  <td className="text-wrap">{list.key}</td>
                  <td className="text-wrap">{list.value}</td>
                  <td className="text-wrap">
                    <button className="btn btn-outline-primary" onClick={() => handleEditClick(list.id, list)}>Edit</button>{" "}
                    <button className="btn btn-outline-danger" onClick={() => handleDeleteClick(list.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
        </div>
      </div>
    </div>
  );
}
