"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { TaskDetail } from "@/components/task-details";
import { useAuth } from "@/context/auth-context";
import { SharedLayout } from "@/components/shared-layout";

type User = {
  id: number;
  name: string;
  role: string;
};

export default function TaskDetailPage() {
  const { taskId } = useParams();
  const { user, isAuthLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthLoading && user === null) {
      router.push("/login");
    }
  }, [user, isAuthLoading, router]);

  if (isAuthLoading) {
    return (
      <SharedLayout>
        <div className="p-8 min-h-screen w-full">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-center items-center h-64">
              <p className="text-black">Ładowanie sesji...</p>
            </div>
          </div>
        </div>
      </SharedLayout>
    );
  }

  if (user === null) {
    return (
      <SharedLayout>
        <div className="p-8 min-h-screen w-full">
          <div className="max-w-6xl mx-auto">
            <div className="flex justify-center items-center h-64">
              <p className="text-black">Przekierowywanie do logowania...</p>
            </div>
          </div>
        </div>
      </SharedLayout>
    );
  }

  return (
    <SharedLayout>
      <TaskDetail taskId={Number(taskId)} user={user} />
    </SharedLayout>
  );
}
