"use client";

import { useState, useEffect } from "react";
import { useApi } from "@/hooks/use-api";

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

type User = {
  id: number;
  name: string;
  role: string;
};

export const StudentDashboard = ({ user }: { user: User }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [answer, setAnswer] = useState("");

  const { getTasks, completeTask, error: apiError } = useApi();

  useEffect(() => {
    const fetchTasks = async () => {
      setLoading(true);
      setError(null);

      try {
        const tasksData = await getTasks();

        if (tasksData) {
          // Filtruj zadania przypisane do tego studenta
          const studentTasks = tasksData.filter(
            (task) => task.student_id === user.id
          );
          setTasks(studentTasks);
        }
      } catch (err) {
        setError("Nie udało się pobrać zadań. Spróbuj ponownie później.");
        console.error("Student dashboard error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [getTasks, user.id]);

  // Aktualizacja błędu z API
  useEffect(() => {
    if (apiError) {
      setError(apiError);
    }
  }, [apiError]);

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedTask?.id || !answer) return;

    setLoading(true);
    setError(null);

    try {
      const result = await completeTask(selectedTask.id, answer);

      if (result) {
        const tasksData = await getTasks();

        if (tasksData) {
          const studentTasks = tasksData.filter(
            (task) => task.student_id === user.id
          );
          setTasks(studentTasks);
        }

        setSelectedTask(null);
        setAnswer("");
      }
    } catch (err) {
      setError("Nie udało się przesłać rozwiązania. Spróbuj ponownie później.");
      console.error("Submit answer error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    const fetchTasks = async () => {
      setLoading(true);
      setError(null);

      try {
        const tasksData = await getTasks();

        if (tasksData) {
          const studentTasks = tasksData.filter(
            (task) => task.student_id === user.id
          );
          setTasks(studentTasks);
        }
      } catch (err) {
        setError("Nie udało się pobrać zadań. Spróbuj ponownie później.");
        console.error("Student dashboard error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Witaj, {user.name}</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
          <p>{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            className="mt-2 text-sm underline"
          >
            Spróbuj ponownie
          </button>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Twoje zadania</h2>

        {loading ? (
          <div className="flex justify-center items-center py-8">
            <p>Ładowanie zadań...</p>
          </div>
        ) : tasks.length === 0 ? (
          <p className="text-gray-500 py-4">Nie masz przypisanych zadań</p>
        ) : (
          <div className="space-y-6">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{task.content}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      Termin oddania: {task.due_date}
                    </p>
                    <p className="text-sm text-gray-500">
                      Maksymalna liczba punktów: {task.max_points}
                    </p>
                  </div>

                  <div>
                    {task.answer ? (
                      task.grade !== undefined ? (
                        <div className="text-right">
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Ocenione
                          </span>
                          <p className="mt-2 font-medium">
                            Ocena: {task.grade}/{task.max_points}
                          </p>
                          {task.comment && (
                            <p className="text-sm text-gray-600 mt-1">
                              Komentarz: {task.comment}
                            </p>
                          )}
                        </div>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                          Oddane - oczekuje na ocenę
                        </span>
                      )
                    ) : (
                      <button
                        type="button"
                        onClick={() => setSelectedTask(task)}
                        className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg disabled:bg-gray-400"
                        disabled={loading}
                      >
                        Prześlij rozwiązanie
                      </button>
                    )}
                  </div>
                </div>

                {task.answer && !task.grade && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-md">
                    <p className="text-sm font-medium">Twoja odpowiedź:</p>
                    <p className="text-sm mt-1">{task.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full">
            <h3 className="text-xl font-semibold mb-4">Prześlij rozwiązanie</h3>
            <p className="mb-4">{selectedTask.content}</p>

            <form onSubmit={handleSubmitAnswer} className="space-y-4">
              <div>
                <label
                  htmlFor="answer"
                  className="block text-sm font-medium mb-1"
                >
                  Twoja odpowiedź
                </label>
                <textarea
                  id="answer"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  rows={5}
                  required
                  disabled={loading}
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedTask(null);
                    setAnswer("");
                  }}
                  className="border border-gray-300 bg-white text-gray-700 py-2 px-4 rounded-lg"
                  disabled={loading}
                >
                  Anuluj
                </button>
                <button
                  type="submit"
                  className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg disabled:bg-gray-400"
                  disabled={loading || !answer.trim()}
                >
                  {loading ? "Wysyłanie..." : "Prześlij"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
