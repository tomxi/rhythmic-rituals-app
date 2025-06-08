document.addEventListener('DOMContentLoaded', () => {
    const notesContainer = document.getElementById('notes-container');
    const apiUrl = 'https://rhythmic-rituals-api.vercel.app/api/notes';

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(responseData => { // Renamed 'notes' to 'responseData' for clarity
            if (Array.isArray(responseData)) { // Check if the response itself is an array
                if (responseData.length === 0) {
                    notesContainer.innerHTML = '<p>No notes found.</p>';
                    return;
                }
                responseData.forEach(note => {
                    const noteElement = document.createElement('div');
                    noteElement.classList.add('note');

                    const titleElement = document.createElement('h2');
                    titleElement.textContent = note.title || 'Untitled Note'; // Handle missing titles

                    const contentElement = document.createElement('p');
                    // Ensure content is treated as text, not HTML
                    contentElement.textContent = note.content || 'No content.'; // Handle missing content

                    noteElement.appendChild(titleElement);
                    noteElement.appendChild(contentElement);
                    notesContainer.appendChild(noteElement);
                });
            } else {
                console.error('API response is not in the expected array format:', responseData);
                notesContainer.innerHTML = '<p>Error: Could not parse notes data. Expected an array.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching notes:', error);
            notesContainer.innerHTML = `<p>Error loading notes: ${error.message}. Please try again later.</p>`;
        });
});
