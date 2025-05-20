"use client";

import { useState, useEffect } from "react";
import { useApi } from "@/hooks/use-api";
import { useRouter } from "next/navigation";

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

export const TaskDetail = ({
  taskId,
  user,
}: {
  taskId: number;
  user: User;
}) => {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [grade, setGrade] = useState<number | "">("");
  const [comment, setComment] = useState("");
  const router = useRouter();

  const { getTaskDetails, completeTask, gradeTask, error: apiError } = useApi();

  useEffect(() => {
    const fetchTaskDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        const taskData = await getTaskDetails(taskId);

        if (taskData) {
          setTask(taskData);
          if (taskData.answer) {
            setAnswer(taskData.answer);
          }
          if (taskData.grade !== null && taskData.grade !== undefined) {
            setGrade(taskData.grade);
          } else {
            setGrade("");
          }
          if (taskData.comment) {
            setComment(taskData.comment);
          }
        } else {
          setError(
            "Nie znaleziono zadania lub brak uprawnień do jego wyświetlenia"
          );
        }
      } catch (err) {
        setError("Nie udało się pobrać szczegółów zadania");
        console.error("Task detail error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTaskDetails();
  }, [getTaskDetails, taskId]);

  useEffect(() => {
    if (apiError) {
      setError(apiError);
    }
  }, [apiError]);

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await completeTask(taskId, answer);

      if (result) {
        const updatedTask = await getTaskDetails(taskId);
        if (updatedTask) {
          setTask(updatedTask);
        }
      }
    } catch (err) {
      setError("Nie udało się przesłać rozwiązania");
      console.error("Submit answer error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGradeTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (grade === "" || typeof grade !== "number") return;

    setLoading(true);
    setError(null);

    try {
      const result = await gradeTask(taskId, grade, comment);

      if (result) {
        const updatedTask = await getTaskDetails(taskId);
        if (updatedTask) {
          setTask(updatedTask);
        }
      }
    } catch (err) {
      setError("Nie udało się ocenić zadania");
      console.error("Grade task error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    const fetchTaskDetails = async () => {
      setLoading(true);
      setError(null);

      try {
        const taskData = await getTaskDetails(taskId);

        if (taskData) {
          setTask(taskData);
        } else {
          setError(
            "Nie znaleziono zadania lub brak uprawnień do jego wyświetlenia"
          );
        }
      } catch (err) {
        setError("Nie udało się pobrać szczegółów zadania");
        console.error("Task detail error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTaskDetails();
  };

  const handleBack = () => {
    router.back();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <p className="text-black">Ładowanie zadania...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-black p-4 rounded-lg mb-6">
        <p>{error}</p>
        <div className="mt-4 flex space-x-2">
          <button
            type="button"
            onClick={handleRetry}
            className="px-4 py-2 bg-[#2C2C2C] text-white rounded-lg"
          >
            Spróbuj ponownie
          </button>
          <button
            type="button"
            onClick={handleBack}
            className="px-4 py-2 border border-gray-300 rounded-lg text-black"
          >
            Powrót
          </button>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="bg-red-50 border border-red-200 text-black p-4 rounded-lg mb-6">
        <p>Nie znaleziono zadania lub brak uprawnień do jego wyświetlenia</p>
        <button
          type="button"
          onClick={handleBack}
          className="mt-4 px-4 py-2 border border-gray-300 rounded-lg text-black"
        >
          Powrót
        </button>
      </div>
    );
  }

  const isStudent = user.role === "student";
  const isTeacher = user.role === "teacher";
  const canSubmitAnswer = isStudent && !task.answer;
  const canEditAnswer = isStudent && task.answer && task.grade === null;
  const canGrade = isTeacher && task.answer && task.grade === null;

  return (
    <div className="w-full h-full">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-black">Szczegóły zadania</h1>
        <button
          type="button"
          onClick={handleBack}
          className="px-4 py-2 border border-gray-300 rounded-lg text-black"
        >
          Powrót
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-xl font-semibold mb-4 text-black">
              Informacje o zadaniu
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Treść zadania:
                </p>
                <p className="text-black">{task.content}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Termin oddania:
                </p>
                <p className="text-black">{task.due_date}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">
                  Maksymalna liczba punktów:
                </p>
                <p className="text-black">{task.max_points}</p>
              </div>
              {isStudent && (
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Nauczyciel:
                  </p>
                  <p className="text-black">{task.teacher_name}</p>
                </div>
              )}
              {isTeacher && (
                <div>
                  <p className="text-sm font-medium text-gray-500">Student:</p>
                  <p className="text-black">{task.student_name}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-500">Status:</p>
                {task.answer ? (
                  task.grade !== null ? (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Ocenione ({task.grade}/{task.max_points})
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      Oddane - oczekuje na ocenę
                    </span>
                  )
                ) : (
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                    Oczekuje na odpowiedź
                  </span>
                )}
              </div>
              {task.sent_date && (
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    Data przesłania:
                  </p>
                  <p className="text-black">{task.sent_date}</p>
                </div>
              )}
            </div>
          </div>

          <div>
            {(canSubmitAnswer || canEditAnswer) && (
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4 text-black">
                  {canEditAnswer ? "Edytuj odpowiedź" : "Prześlij odpowiedź"}
                </h2>
                <form onSubmit={handleSubmitAnswer} className="space-y-4">
                  <div>
                    <label
                      htmlFor="answer"
                      className="block text-sm font-medium mb-1 text-black"
                    >
                      Twoja odpowiedź
                    </label>
                    <textarea
                      id="answer"
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                      rows={5}
                      required
                      disabled={loading}
                    />
                  </div>
                  <button
                    type="submit"
                    className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg disabled:bg-gray-400"
                    disabled={loading || !answer.trim()}
                  >
                    {loading
                      ? "Wysyłanie..."
                      : canEditAnswer
                      ? "Aktualizuj"
                      : "Wyślij"}
                  </button>
                </form>
              </div>
            )}

            {task.answer && (
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4 text-black">
                  Odpowiedź
                </h2>
                <div className="p-4 bg-gray-50 rounded-md">
                  <p className="text-black whitespace-pre-wrap">
                    {task.answer}
                  </p>
                </div>
              </div>
            )}

            {isTeacher && task.answer && task.grade === null && (
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4 text-black">
                  Oceń zadanie
                </h2>
                <form onSubmit={handleGradeTask} className="space-y-4">
                  <div>
                    <label
                      htmlFor="grade"
                      className="block text-sm font-medium mb-1 text-black"
                    >
                      Ocena (0-{task.max_points})
                    </label>
                    <input
                      id="grade"
                      type="number"
                      min={0}
                      max={task.max_points}
                      value={grade}
                      onChange={(e) => {
                        const value = e.target.value;
                        if (value === "") {
                          setGrade("");
                        } else {
                          const numValue = Number.parseInt(value, 10);
                          if (
                            !Number.isNaN(numValue) &&
                            numValue >= 0 &&
                            numValue <= (task.max_points || 0)
                          ) {
                            setGrade(numValue);
                          }
                        }
                      }}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                      required
                      disabled={loading}
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="comment"
                      className="block text-sm font-medium mb-1 text-black"
                    >
                      Komentarz (opcjonalnie)
                    </label>
                    <textarea
                      id="comment"
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-black"
                      rows={3}
                      disabled={loading}
                      placeholder="Wprowadź komentarz do oceny..."
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="submit"
                      className="bg-[#2C2C2C] text-white py-2 px-4 rounded-lg disabled:bg-gray-400"
                      disabled={loading || grade === ""}
                    >
                      {loading ? "Zapisywanie..." : "Oceń zadanie"}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {task.grade !== null && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-black">Ocena</h2>
                <div className="p-4 bg-gray-50 rounded-md">
                  <p className="text-black font-medium">
                    Punkty: {task.grade}/{task.max_points}
                  </p>
                  {task.comment && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-gray-500">
                        Komentarz:
                      </p>
                      <p className="text-black">{task.comment}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
