import type { ReactNode } from "react";
import { Header } from "./Header";
import { useAuth } from "@/context/auth-context";

type SharedLayoutProps = {
  children: ReactNode;
};

export const SharedLayout = ({ children }: SharedLayoutProps) => {
  const { logout } = useAuth();

  return (
    <div className="p-8 min-h-screen w-full">
      <div className="max-w-6xl mx-auto">
        <Header onLogout={logout} />
        {children}
      </div>
    </div>
  );
};
