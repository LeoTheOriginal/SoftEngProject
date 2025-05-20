"use client";

import { useEffect, useState } from "react";
import { useParams, redirect } from "next/navigation";
import { TaskDetail } from "@/components/TaskDetail";
import { useAuth } from "@/context/auth-context";
import { SharedLayout } from "@/components/SharedLayout";

type User = {
  id: number;
  name: string;
  role: string;
};

export default function TaskDetailPage() {
  const { taskId } = useParams();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Sprawdzamy, czy użytkownik jest zalogowany
    if (user === null) {
      redirect("/login");
    } else {
      setIsLoading(false);
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className="p-8 min-h-screen w-full">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-center items-center h-64">
            <p className="text-black">Ładowanie...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <SharedLayout>
      {user && <TaskDetail taskId={Number(taskId)} user={user} />}
    </SharedLayout>
  );
}
