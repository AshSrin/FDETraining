import { useState, useEffect } from "react";
import type { encounterInterface } from "./types";
import Header from "./components/Header";

import Pagination from "./components/Pagination";

//import { API_BASE } from "week3_miniProject_with_HTML/config";
//include logic for pagination so the user can navigate through the pages of encounter data. The current page and total pages should be tracked in the state, and the onPageChange function should update the current page when the user clicks on the pagination buttons.
//The Pagination component should be used to display the encounter data in a paginated format, allowing the user to navigate through the pages of encounter data. Maximum of 40 encounters should be displayed per page. The current page and total pages should be tracked in the state, and the onPageChange function should update the current page when the user clicks on the pagination buttons.  
function App() {
  const [encounter, setEncounter] = useState<encounterInterface[] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const encountersPerPage = 40;

  useEffect(() => {
   fetch('http://127.0.0.1:8001/encounters')
      .then((response) => response.json())
      .then((data) => setEncounter(Array.isArray(data) ? data : [data]))
      .catch((error) => console.error("Failed to fetch encounter:", error));
  }, []);

  const totalPages = encounter ? Math.ceil(encounter.length / encountersPerPage) : 1;   

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const indexOfLastEncounter = currentPage * encountersPerPage;
  const indexOfFirstEncounter = indexOfLastEncounter - encountersPerPage;
  const currentEncounters = encounter ? encounter.slice(indexOfFirstEncounter, indexOfLastEncounter) : [];

  return (
    <div className="App">
      <Header />
      {encounter ? (
        <Pagination
          encounter={currentEncounters}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      ) : (
        <p>Loading encounter data...</p>
      )}
    </div>
  );
}

export default App;