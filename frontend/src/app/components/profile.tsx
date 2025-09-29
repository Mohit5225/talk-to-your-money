import { UserProfile } from '@clerk/nextjs';

export default function ProfilePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Your Profile</h1>
      <UserProfile 
        path="/profile"
        routing="path"
        appearance={{
          elements: {
            rootBox: "mx-auto"
          }
        }}
      />
    </div>
  );
}