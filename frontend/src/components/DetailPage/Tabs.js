import React from "react";
import LookUp from "./LookUpTable";
import UrlTable from "./UrlTable";
import { useNavigate } from "react-router-dom";
import WebScrapping from "../WebScrapping/WebScrapping";


export default function Tabs() {
    const navigate = useNavigate();
  
  return (
    <div>
      <br/>
      <div>
          <button
            className="btn btn-primary me-4"
            onClick={() => navigate("/lookuptable")}
          >
            {" "}
            Goto add list page
          </button>
          <button className="btn btn-primary" onClick={() => navigate("/urlList")}>
            Goto add URL page
          </button>
        </div>
        <br/>
      <nav>
        <div className="nav nav-tabs" id="nav-tab" role="tablist">
          <button
            className="nav-link active"
            id="nav-urlList-tab"
            data-bs-toggle="tab"
            data-bs-target="#nav-urlList"
            type="button"
            role="tab"
            aria-controls="nav-urlList"
            aria-selected="true"
          >
            Url list 
          </button>
          <button
            className="nav-link"
            id="nav-lookuplist-tab"
            data-bs-toggle="tab"
            data-bs-target="#nav-lookuplist"
            type="button"
            role="tab"
            aria-controls="nav-lookuplist"
            aria-selected="false"
          >
            Look up list
          </button>
          <button
            className="nav-link"
            id="nav-webscrapping-tab"
            data-bs-toggle="tab"
            data-bs-target="#nav-webscrapping"
            type="button"
            role="tab"
            aria-controls="nav-webscrapping"
            aria-selected="false"
          >
            Web Scrapping
          </button>
          
        </div>
      </nav>
      <div className="tab-content" id="nav-tabContent">
        <div
          className="tab-pane fade show active"
          id="nav-urlList"
          role="tabpanel"
          aria-labelledby="nav-urlList-tab"
        >
         <UrlTable />
        </div>
        <div
          className="tab-pane fade"
          id="nav-lookuplist"
          role="tabpanel"
          aria-labelledby="nav-lookuplist-tab"
        >
           <LookUp />
        </div>
        <div
          className="tab-pane fade"
          id="nav-webscrapping"
          role="tabpanel"
          aria-labelledby="nav-webscrapping-tab"
        >
           <WebScrapping />
        </div>
        
      </div>
      
    </div>
  );
}
