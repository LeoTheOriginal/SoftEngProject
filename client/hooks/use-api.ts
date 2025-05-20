"use client";

import { useState, useCallback } from "react";

const API_URL = "http://127.0.0.1:5000";

type ApiOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: Record<string, unknown> | FormData;
  headers?: Record<string, string>;
  credentials?: RequestCredentials;
  queryParams?: Record<string, string>;
};

type AuthData = {
  email: string;
  password: string;
  name?: string;
  surname?: string;
  role?: string;
};

type Task = {
  id?: number;
  content?: string;
  student_id?: number;
  teacher_id?: number;
  due_date?: string;
  sent_date?: string;
  completed?: boolean;
  max_points?: number;
  answer?: string;
  grade?: number;
  comment?: string;
  file_path?: string;
  student_name?: string;
  teacher_name?: string;
};

type User = {
  id: number;
  name: string;
  role: string;
};

type LogEntry = {
  id: number;
  user: string;
  action: string;
  timestamp: string;
};

export const useApi = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window !== "undefined") {
      const savedUser = localStorage.getItem("user");
      console.log("Inicjalizacja użytkownika z localStorage:", savedUser);
      return savedUser ? JSON.parse(savedUser) : null;
    }
    return null;
  });

  const fetchApi = useCallback(
    async <T>(
      endpoint: string,
      options: ApiOptions = {}
    ): Promise<T | null> => {
      const {
        method = "GET",
        body,
        headers = {},
        credentials = "include",
        queryParams = {},
      } = options;

      try {
        setLoading(true);
        setError(null);

        let url = `${API_URL}${endpoint}`;

        if (Object.keys(queryParams).length > 0) {
          const params = new URLSearchParams();
          for (const [key, value] of Object.entries(queryParams)) {
            if (value) params.append(key, value);
          }
          url += `?${params.toString()}`;
        }

        console.log(`Wykonuję zapytanie do: ${url}`, {
          method,
          body,
          queryParams,
        });

        const requestOptions: RequestInit = {
          method,
          credentials,
          headers: {
            "Content-Type": "application/json",
            ...headers,
          },
          mode: "cors",
        };

        if (body) {
          requestOptions.body = JSON.stringify(body);
        }

        const response = await fetch(url, requestOptions);

        if (!response.ok) {
          const errorData = await response
            .json()
            .catch(() => ({ message: `Błąd HTTP: ${response.status}` }));
          throw new Error(errorData.message || `Błąd HTTP: ${response.status}`);
        }

        const data = await response.json();
        console.log(`Odpowiedź z ${endpoint}:`, data);
        return data as T;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Nieznany błąd";
        setError(errorMessage);
        console.error(`API Error (${endpoint}):`, err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const login = useCallback(
    async (credentials: { email: string; password: string }) => {
      const result = await fetchApi<{
        message: string;
        user: { id: number; name: string; role: string };
      }>("/login", {
        method: "POST",
        body: credentials,
      });

      if (result?.user) {
        console.log("Zapisuję dane użytkownika:", result.user);
        setUser(result.user);
        if (typeof window !== "undefined") {
          localStorage.setItem("user", JSON.stringify(result.user));
          console.log("Dane użytkownika zapisane w localStorage");
        }
      }

      return result;
    },
    [fetchApi]
  );

  const register = useCallback(
    async (userData: AuthData) => {
      return fetchApi<{ message: string }>("/register", {
        method: "POST",
        body: userData,
      });
    },
    [fetchApi]
  );

  const logout = useCallback(async () => {
    const result = await fetchApi<{ message: string }>("/logout", {
      method: "POST",
    });

    if (result) {
      setUser(null);
      if (typeof window !== "undefined") {
        localStorage.removeItem("user");
      }
    }

    return result;
  }, [fetchApi]);

  const getTasks = useCallback(async () => {
    if (!user) {
      console.error("Nie można pobrać zadań - brak zalogowanego użytkownika");
      return [];
    }

    console.log("Pobieranie zadań dla użytkownika:", user);

    try {
      return await fetchApi<Task[]>("/tasks", {
        queryParams: {
          user_id: user.id.toString(),
          role: user.role,
        },
      });
    } catch (err) {
      console.error("Error fetching tasks:", err);
      return [];
    }
  }, [fetchApi, user]);

  const createTask = useCallback(
    async (taskData: Task) => {
      if (!user) return null;

      try {
        return await fetchApi<{ message: string }>("/tasks", {
          method: "POST",
          body: {
            ...taskData,
            teacher_id: user.id,
          } as Record<string, unknown>,
        });
      } catch (err) {
        console.error("Error creating task:", err);
        return null;
      }
    },
    [fetchApi, user]
  );

  const completeTask = useCallback(
    async (taskId: number, answer: string) => {
      if (!user) return null;

      try {
        return await fetchApi<{ message: string }>(`/task/complete/${taskId}`, {
          method: "POST",
          body: {
            answer,
            student_id: user.id,
          },
        });
      } catch (err) {
        console.error("Error completing task:", err);
        return null;
      }
    },
    [fetchApi, user]
  );

  const gradeTask = useCallback(
    async (taskId: number, grade: number, comment?: string) => {
      if (!user) return null;

      try {
        return await fetchApi<{ message: string }>(`/task/grade/${taskId}`, {
          method: "POST",
          body: {
            grade,
            comment,
            teacher_id: user.id,
          },
        });
      } catch (err) {
        console.error("Error grading task:", err);
        return null;
      }
    },
    [fetchApi, user]
  );

  const getStudents = useCallback(async () => {
    try {
      return await fetchApi<{ id: number; name: string }[]>("/students");
    } catch (err) {
      console.error("Error fetching students:", err);
      return [];
    }
  }, [fetchApi]);

  const uploadFile = useCallback(
    async (taskId: number, file: File) => {
      if (!user) return null;

      const formData = new FormData();
      formData.append("file", file);
      formData.append("student_id", user.id.toString());

      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_URL}/upload/${taskId}`, {
          method: "POST",
          credentials: "include",
          mode: "cors",
          body: formData,
        });

        const data = await response.json();
        return data;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Nieznany błąd";
        setError(errorMessage);
        console.error("Upload Error:", err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [user]
  );

  const getLogs = useCallback(async () => {
    if (!user || user.role !== "admin") return [];

    try {
      return await fetchApi<LogEntry[]>("/logs", {
        queryParams: {
          admin_id: user.id.toString(),
        },
      });
    } catch (err) {
      console.error("Error fetching logs:", err);
      return [];
    }
  }, [fetchApi, user]);

  const getTaskDetails = useCallback(
    async (taskId: number) => {
      if (!user) {
        console.error(
          "Nie można pobrać szczegółów zadania - brak zalogowanego użytkownika"
        );
        return null;
      }

      try {
        return await fetchApi<Task>(`/task/${taskId}`, {
          queryParams: {
            user_id: user.id.toString(),
            role: user.role,
          },
        });
      } catch (err) {
        console.error("Error fetching task details:", err);
        return null;
      }
    },
    [fetchApi, user]
  );

  return {
    loading,
    error,
    user,
    login,
    register,
    logout,
    getTasks,
    createTask,
    completeTask,
    gradeTask,
    getStudents,
    uploadFile,
    getLogs,
    getTaskDetails,
  };
};
