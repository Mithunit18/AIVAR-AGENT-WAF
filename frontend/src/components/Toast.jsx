import { useEffect } from 'react';
import { CheckCircle, AlertTriangle, X, Info } from 'lucide-react';

export function Toast({ message, type = 'info', onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const styles = {
    success: "bg-emerald-950 border-emerald-500/30 text-emerald-400",
    error: "bg-rose-950 border-rose-500/30 text-rose-400",
    warning: "bg-amber-950 border-amber-500/30 text-amber-400",
    info: "bg-sky-950 border-sky-500/30 text-sky-400",
  };

  const icons = {
    success: <CheckCircle size={18} />,
    error: <AlertTriangle size={18} />,
    warning: <AlertTriangle size={18} />,
    info: <Info size={18} />,
  };

  return (
    <div className={`fixed bottom-6 right-6 flex items-center gap-3 px-4 py-3 rounded-lg border shadow-xl animate-in slide-in-from-bottom-5 duration-300 z-50 ${styles[type]}`}>
      {icons[type]}
      <p className="text-sm font-medium">{message}</p>
      <button onClick={onClose} className="ml-4 opacity-70 hover:opacity-100 transition-opacity">
        <X size={16} />
      </button>
    </div>
  );
}
