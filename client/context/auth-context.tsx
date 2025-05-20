"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { useApi } from "@/hooks/use-api";

type User = {
  id: number;
  name: string;
  role: string;
};

type AuthContextType = {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (
    email: string,
    password: string,
    name: string,
    surname: string,
    role: string
  ) => Promise<boolean>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const {
    login: apiLogin,
    register: apiRegister,
    logout: apiLogout,
    loading,
    error,
  } = useApi();
  const router = useRouter();

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem("user");
      }
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    const response = await apiLogin({ email, password });

    if (response?.user) {
      setUser(response.user);
      localStorage.setItem("user", JSON.stringify(response.user));
      return true;
    }

    return false;
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    surname: string,
    role: string
  ): Promise<boolean> => {
    const response = await apiRegister({
      email,
      password,
      name,
      surname,
      role,
    });
    return !!response;
  };

  const logout = async (): Promise<void> => {
    await apiLogout();
    setUser(null);
    localStorage.removeItem("user");
    router.push("/");
  };

  return (
    <AuthContext.Provider
      value={{ user, login, register, logout, loading, error }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
