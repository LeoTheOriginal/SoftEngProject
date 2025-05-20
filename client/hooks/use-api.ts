"use client";

import { useState, useCallback } from "react";

const API_URL = "http://127.0.0.1:5000";

type ApiOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: Record<string, unknown> | FormData;
  headers?: Record<string, string>;
  credentials?: RequestCredentials;
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
  due_date?: string;
  max_points?: number;
  answer?: string;
  grade?: number;
  comment?: string;
};

export const useApi = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

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
      } = options;

      try {
        setLoading(true);
        setError(null);

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

        const response = await fetch(`${API_URL}${endpoint}`, requestOptions);

        if (!response.ok) {
          try {
            const errorData = await response.json();
            throw new Error(
              errorData.message || `Błąd HTTP: ${response.status}`
            );
          } catch (jsonError) {
            throw new Error(`Błąd HTTP: ${response.status}`);
          }
        }

        const data = await response.json();
        return data as T;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Nieznany błąd";
        setError(errorMessage);
        console.error("API Error:", err);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const login = useCallback(
    async (credentials: { email: string; password: string }) => {
      return fetchApi<{
        message: string;
        user: { id: number; name: string; role: string };
      }>("/login", {
        method: "POST",
        body: credentials,
      });
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
    return fetchApi<{ message: string }>("/logout");
  }, [fetchApi]);

  const getTasks = useCallback(async () => {
    try {
      return await fetchApi<Task[]>("/tasks");
    } catch (err) {
      console.error("Error fetching tasks:", err);
      return [];
    }
  }, [fetchApi]);

  const createTask = useCallback(
    async (taskData: Task) => {
      try {
        return await fetchApi<{ message: string }>("/tasks", {
          method: "POST",
          body: taskData as Record<string, unknown>,
        });
      } catch (err) {
        console.error("Error creating task:", err);
        return null;
      }
    },
    [fetchApi]
  );

  const completeTask = useCallback(
    async (taskId: number, answer: string) => {
      try {
        return await fetchApi<{ message: string }>(`/task/complete/${taskId}`, {
          method: "POST",
          body: { answer },
        });
      } catch (err) {
        console.error("Error completing task:", err);
        return null;
      }
    },
    [fetchApi]
  );

  const gradeTask = useCallback(
    async (taskId: number, grade: number, comment?: string) => {
      try {
        return await fetchApi<{ message: string }>(`/task/grade/${taskId}`, {
          method: "POST",
          body: { grade, comment },
        });
      } catch (err) {
        console.error("Error grading task:", err);
        return null;
      }
    },
    [fetchApi]
  );

  const getStudents = useCallback(async () => {
    try {
      return await fetchApi<{ id: number; name: string }[]>("/students");
    } catch (err) {
      console.error("Error fetching students:", err);
      return [];
    }
  }, [fetchApi]);

  const uploadFile = useCallback(async (taskId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/upload/${taskId}`, {
        method: "POST",
        credentials: "include",
        mode: "cors",
        body: formData,
      });

      if (!response.ok) {
        try {
          const errorData = await response.json();
          throw new Error(errorData.message || `Błąd HTTP: ${response.status}`);
        } catch (jsonError) {
          throw new Error(`Błąd HTTP: ${response.status}`);
        }
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Nieznany błąd";
      setError(errorMessage);
      console.error("Upload Error:", err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    login,
    register,
    logout,
    getTasks,
    createTask,
    completeTask,
    gradeTask,
    getStudents,
    uploadFile,
  };
};
