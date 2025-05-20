import { useAuth } from "@/context/auth-context";

type HeaderProps = {
  onLogout: () => void;
};

export const Header = ({ onLogout }: HeaderProps) => {
  return (
    <div className="flex justify-between items-center mb-6">
      <h1 className="text-3xl text-black font-bold">
        Platforma e-learningowa
      </h1>
      <button
        onClick={onLogout}
        className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg"
        type="button"
      >
        Wyloguj
      </button>
    </div>
  );
}; 