import React from "react";
import {
  BrowserRouter,
  BrowserRouter as Router,
  Route,
  Routes
} from "react-router-dom";
import UrlList from "../URLList/UrlList";
import LookupList from "../LookupTable/LookupList";
import Tabs from "../DetailPage/Tabs";

export default function Navbar() {
  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            <img src="https://www.robosoftin.com/assets/image/common/Robosoft_main-logo_horizontal.svg" />
          </a>
        </div>
      </nav>
      <BrowserRouter>
        <Routes>
          <Route path="/urlList"  element={<UrlList />} />
          <Route path="/lookuptable" element={<LookupList />} />
          <Route path="/" exact element={<Tabs />} />
          <Route path="/urlList/:id" element={<UrlList />} />
          <Route path="/lookuptable/:id" element={<LookupList />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}
