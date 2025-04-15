"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login, loading, error } = useAuth();
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success) {
      router.push("/dashboard");
    }
  };

  return (
    <div className="">
      <h2 className="text-black text-4xl font-bold text-center mb-6">
        Podaj dane do logowania
      </h2>

      <form
        onSubmit={handleLogin}
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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Podaj hasło"
            className="w-full px-3 py-2 border border-[#D9D9D9] rounded-lg text-black focus:outline-none"
            required
          />
        </div>

        {error && <div className="text-red-500 text-sm mt-2">{error}</div>}

        <button
          type="submit"
          className="mt-4 py-2 px-4 bg-[#2C2C2C] text-white font-medium rounded-lg disabled:bg-gray-400"
          disabled={loading}
        >
          {loading ? "Logowanie..." : "Zaloguj się"}
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
