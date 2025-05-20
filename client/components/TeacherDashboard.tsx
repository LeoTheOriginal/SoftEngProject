"use client";

import { useState, useEffect } from "react";
import { useApi } from "@/hooks/use-api";
import Link from "next/link";

type Student = {
  id: number;
  name: string;
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
  student_name?: string;
};

type User = {
  id: number;
  name: string;
  role: string;
};

export const TeacherDashboard = ({ user }: { user: User }) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTask, setNewTask] = useState<Task>({
    content: "",
    student_id: undefined,
    due_date: "",
    max_points: 10,
  });

  const { getStudents, getTasks, createTask, error: apiError } = useApi();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const studentsData = await getStudents();
        const tasksData = await getTasks();

        if (studentsData) setStudents(studentsData);
        if (tasksData) setTasks(tasksData);
      } catch (err) {
        setError("Nie udało się pobrać danych. Spróbuj ponownie później.");
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [getStudents, getTasks]);

  // Aktualizacja błędu z API
  useEffect(() => {
    if (apiError) {
      setError(apiError);
    }
  }, [apiError]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.content || !newTask.student_id || !newTask.due_date) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await createTask(newTask);
      if (result) {
        const updatedTasks = await getTasks();
        if (updatedTasks) setTasks(updatedTasks);

        setNewTask({
          content: "",
          student_id: undefined,
          due_date: "",
          max_points: 10,
        });
      }
    } catch (err) {
      setError("Nie udało się utworzyć zadania. Spróbuj ponownie później.");
      console.error("Create task error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const studentsData = await getStudents();
        const tasksData = await getTasks();

        if (studentsData) setStudents(studentsData);
        if (tasksData) setTasks(tasksData);
      } catch (err) {
        setError("Nie udało się pobrać danych. Spróbuj ponownie później.");
        console.error("Dashboard error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  };

  return (
    <div className="h-full">
      <h1 className="text-3xl font-bold mb-6 text-black">Witaj, {user.name}</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-black p-4 rounded-lg mb-6">
          <p>{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            className="mt-2 text-sm underline text-black"
          >
            Spróbuj ponownie
          </button>
        </div>
      )}

      <div className="flex gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm w-1/2">
          <h2 className="text-xl font-semibold mb-4 text-black">
            Przypisz nowe zadanie
          </h2>
          <form
            onSubmit={handleCreateTask}
            className="space-y-4 h-[calc(100%-50px)] overflow-y-auto"
          >
            <div>
              <label
                htmlFor="student"
                className="block text-sm font-medium mb-1 text-black"
              >
                Student
              </label>
              <select
                id="student"
                value={newTask.student_id || ""}
                onChange={(e) =>
                  setNewTask({ ...newTask, student_id: Number(e.target.value) })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                required
                disabled={loading || students.length === 0}
              >
                <option value="">Wybierz studenta</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="content"
                className="block text-sm font-medium mb-1 text-black"
              >
                Treść zadania
              </label>
              <textarea
                id="content"
                value={newTask.content || ""}
                onChange={(e) =>
                  setNewTask({ ...newTask, content: e.target.value })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                rows={3}
                required
                disabled={loading}
              />
            </div>

            <div>
              <label
                htmlFor="due_date"
                className="block text-sm font-medium mb-1 text-black"
              >
                Termin oddania
              </label>
              <input
                id="due_date"
                type="date"
                value={newTask.due_date || ""}
                onChange={(e) =>
                  setNewTask({ ...newTask, due_date: e.target.value })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label
                htmlFor="max_points"
                className="block text-sm font-medium mb-1 text-black"
              >
                Maksymalna liczba punktów
              </label>
              <input
                id="max_points"
                type="number"
                value={newTask.max_points || 10}
                onChange={(e) =>
                  setNewTask({ ...newTask, max_points: Number(e.target.value) })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                min={1}
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg disabled:bg-gray-400"
              disabled={loading || students.length === 0}
            >
              {loading ? "Dodawanie..." : "Dodaj zadanie"}
            </button>
          </form>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm w-1/2">
          <h2 className="text-xl font-semibold mb-4 text-black">
            Zadania przypisane studentom
          </h2>
          <div className="h-[calc(100%-50px)] overflow-y-auto">
            {loading ? (
              <div className="flex justify-center items-center py-8">
                <p className="text-black">Ładowanie danych...</p>
              </div>
            ) : tasks.length === 0 ? (
              <p className="text-black py-4">Brak przypisanych zadań</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Student
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Zadanie
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Termin
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Punkty
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                        Akcje
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tasks.map((task) => {
                      const studentName =
                        task.student_name ||
                        (() => {
                          const student = students.find(
                            (s) => s.id === task.student_id
                          );
                          return student?.name || "Nieznany";
                        })();

                      return (
                        <tr key={task.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-black">
                            {studentName}
                          </td>
                          <td className="px-6 py-4 text-black">
                            {task.content}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-black">
                            {task.due_date}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-black">
                            {task.max_points}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {task.answer ? (
                              task.grade !== undefined ? (
                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                  Ocenione ({task.grade}/{task.max_points})
                                </span>
                              ) : (
                                <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                  Do oceny
                                </span>
                              )
                            ) : (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                Oczekuje
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Link
                              href={`/task/${task.id}`}
                              className="text-[#2C2C2C] hover:underline"
                            >
                              Szczegóły
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
