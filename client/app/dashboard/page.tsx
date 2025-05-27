"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { TeacherDashboard } from "@/components/teacher-dashboard";
import { StudentDashboard } from "@/components/student-dashboard";
import { SharedLayout } from "@/components/shared-layout";

export default function Dashboard() {
  const { user, isAuthLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthLoading && !user) {
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

  if (!user) {
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
      {user.role === "teacher" ? (
        <TeacherDashboard user={user} />
      ) : (
        <StudentDashboard user={user} />
      )}
    </SharedLayout>
  );
}
