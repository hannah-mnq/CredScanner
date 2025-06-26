async function checkFakeNews() {
      const input = document.getElementById('newsInput').value.trim();
      const outputDiv = document.getElementById('output');
      const checkButton = document.getElementById('checkButton');
      const buttonText = document.getElementById('buttonText');

      if (!input) {
        alert("Please enter a headline or URL.");
        return;
      }
      outputDiv.style.display = 'block';
      outputDiv.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing news credibility...</div>';
      outputDiv.className = "result";
      
      checkButton.disabled = true;
      buttonText.innerHTML = '<div class="spinner"></div> Analyzing...';

      try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: input })
        });

        const data = await response.json();

        if (data.error) {
          outputDiv.innerHTML = `<div style="color: #c53030;"><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> ${data.error}</div>`;
          outputDiv.className = "result fake";
          return;
        }

        let resultHTML = `<div style="font-size: 1.2rem; margin-bottom: 1rem;">
          <i class="fas fa-${data.final_verdict.toLowerCase() === 'fake' ? 'times-circle' : 'check-circle'}"></i>
          <strong>Prediction:</strong> <span class="prediction">${data.final_verdict}</span>
        </div>`;

        if (data.extracted) {
          resultHTML += `<div style="margin-bottom: 1rem;">
            <strong><i class="fas fa-extract"></i> Extracted from URL:</strong><br>
            <em style="color: #666;">${data.extracted}</em>
          </div>`;
        }

        if (data.explanation) {
          resultHTML += `<div class="verdict">
            <strong><i class="fas fa-info-circle"></i> Detailed Analysis:</strong><br>
            ${data.explanation}
          </div>`;
        }

        if (data.matched_url) {
          resultHTML += `<div class="link">
            <strong><i class="fas fa-link"></i> Reference Source:</strong><br>
            <a href="${data.matched_url}" target="_blank" rel="noopener noreferrer">${data.matched_url}</a>
          </div>`;
        }

        outputDiv.innerHTML = resultHTML;
        outputDiv.className = "result " + (data.final_verdict.toLowerCase() === "fake" ? "fake" : "real");

      } catch (error) {
        outputDiv.innerHTML = `<div style="color: #c53030;">
          <i class="fas fa-exclamation-triangle"></i> 
          <strong>Connection Error:</strong> Unable to connect to the analysis server. Please check if the backend is running.
        </div>`;
        outputDiv.className = "result fake";
      } finally {
        checkButton.disabled = false;
        buttonText.innerHTML = '<i class="fas fa-search"></i> Analyze News';
      }
    }
    document.getElementById('newsInput').addEventListener('keydown', function(event) {
      if (event.key === 'Enter' && event.ctrlKey) {
        checkFakeNews();
      }
    });