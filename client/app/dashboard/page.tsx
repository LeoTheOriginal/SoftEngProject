"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import Link from "next/link";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  if (!user) {
    return null;
  }

  return (
    <div className="p-8 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm">
              Zalogowano jako: <strong>{user.name}</strong> (
              {user.role === "teacher" ? "Nauczyciel" : "Student"})
            </span>
            <button
              onClick={logout}
              className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg"
              type="button"
            >
              Wyloguj
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Moje zadania</h2>
            <p className="text-gray-600">
              {user.role === "student"
                ? "Tutaj zobaczysz zadania przydzielone przez nauczycieli."
                : "Tutaj zarządzasz zadaniami dla studentów."}
            </p>
            <Link
              href="/dashboard/tasks"
              className="mt-4 inline-block bg-[#2C2C2C] text-white py-2 px-4 rounded-lg"
            >
              Przejdź do zadań
            </Link>
          </div>

          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Mój profil</h2>
            <p className="text-gray-600">
              Zarządzaj swoimi danymi i ustawieniami konta.
            </p>
            <Link
              href="/dashboard/profile"
              className="mt-4 inline-block bg-[#2C2C2C] text-white py-2 px-4 rounded-lg"
            >
              Przejdź do profilu
            </Link>
          </div>

          {user.role === "teacher" && (
            <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <h2 className="text-xl font-semibold mb-4">Moi studenci</h2>
              <p className="text-gray-600">
                Zarządzaj listą swoich studentów i ich postępami.
              </p>
              <Link
                href="/dashboard/students"
                className="mt-4 inline-block bg-[#2C2C2C] text-white py-2 px-4 rounded-lg"
              >
                Przejdź do studentów
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
