/**
 * Sets up an event listener for the "htmx:afterRequest" event on the upload-files-table element.
 * When triggered, it checks if the event target is a file download button and initiates a file download.
 * function
 * listens htmx:afterRequest
 * returns {void}
 */
document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("upload-files-table")
    .addEventListener("htmx:afterRequest", function (evt) {
      if (evt.target && evt.target.id === "file-download-button") {
        const downloadUrl = evt.target.getAttribute("hx-get");
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = ""; // Optional: specify a filename if needed
        document.body.appendChild(a);
        document.body.removeChild(a);
      }
    });
});

// Making a after request function to call and handle the loading state
function handleUploadRequest() {
  try {
    const components = document.querySelectorAll("[x-data]");

    const uploadPageIndex = Array.from(components).findIndex(
      (component) => component.id === "upload-page"
    );

    if (uploadPageIndex === -1) {
      throw new Error("No element with id 'upload-page' found");
    }
    const component = components[uploadPageIndex];
    if (!component) {
      throw new Error("No element with x-data found");
    }
    const data = Alpine.mergeProxies(component._x_dataStack);

    data.isLoading = false;
    data.fileLoaded = false;
    data.fileName = "";
  } catch (error) {
    console.error("Error in click event handler:", error);
  }
}
