"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { TeacherDashboard } from "@/components/TeacherDashboard";
import { StudentDashboard } from "@/components/StudentDashboard";
import { SharedLayout } from "@/components/SharedLayout";

export default function Dashboard() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  if (!user) {
    return null;
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
