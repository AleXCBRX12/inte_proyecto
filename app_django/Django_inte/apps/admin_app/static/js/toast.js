(function(){
  const container = document.getElementById("toastContainer");
  if (!container) return;

  function showToast(message, type="info", timeout=3000){
    const toast = document.createElement("div");
    toast.className = `toast-item toast-${type}`;
    toast.role = "status";
    toast.innerText = message;
    container.appendChild(toast);
    requestAnimationFrame(()=> toast.classList.add("show"));
    setTimeout(()=> {
      toast.classList.remove("show");
      setTimeout(()=> toast.remove(), 200);
    }, timeout);
  }

  window.Toast = { show: showToast };
})();
