"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("student");
  const { register, loading, error } = useAuth();
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await register(email, password, firstName, lastName, role);
    if (success) {
      router.push("/login");
    }
  };

  return (
    <div className="">
      <h2 className="text-black text-4xl font-bold text-center mb-6">
        Rejestracja użytkownika
      </h2>

      <form
        onSubmit={handleRegister}
        className="flex flex-col gap-4 px-12 py-8 rounded-lg shadow-lg border border-[#D9D9D9]"
      >
        <div>
          <label
            htmlFor="email"
            className="block text-black text-sm font-medium mb-1"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            placeholder="Podaj email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-black text-sm font-medium mb-1"
          >
            Hasło
          </label>
          <input
            id="password"
            type="password"
            placeholder="Podaj hasło"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          />
        </div>

        <div>
          <label
            htmlFor="firstName"
            className="block text-black text-sm font-medium mb-1"
          >
            Imię
          </label>
          <input
            id="firstName"
            type="text"
            placeholder="Podaj imię"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          />
        </div>

        <div>
          <label
            htmlFor="lastName"
            className="block text-black text-sm font-medium mb-1"
          >
            Nazwisko
          </label>
          <input
            id="lastName"
            type="text"
            placeholder="Podaj nazwisko"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          />
        </div>

        <div>
          <label
            htmlFor="role"
            className="block text-black text-sm font-medium mb-1"
          >
            Rola
          </label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          >
            <option value="student">Student</option>
            <option value="teacher">Nauczyciel</option>
          </select>
        </div>

        {error && <div className="text-red-500 text-sm mt-2">{error}</div>}

        <button
          type="submit"
          className="mt-4 py-2 px-4 bg-[#2C2C2C] text-white font-medium rounded-lg disabled:bg-gray-400"
          disabled={loading}
        >
          {loading ? "Rejestracja..." : "Zarejestruj się"}
        </button>

        <div className="text-center mt-4">
          <Link href="/" className="text-black hover:underline">
            Powrót do strony głównej
          </Link>
        </div>
      </form>
    </div>
  );
}
