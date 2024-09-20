import { ModeToggle } from "@/components/mode-toggle";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
function Register() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [hashed_password, sethashed_password] = useState("");
    const [balance, setBalance] = useState("");
    // Add your form submit handler here

    const submitRegister = async () => {
        const requestOptions = {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: username,
            email: email,
            hashed_password: password,
            balance: balance,
            role: "customer", 
            net_stock: 0       
          }),
        };
    
        const response = await fetch("http://localhost:8000/api/auth/register", requestOptions);
        const data = await response.json();
    
        if (!response.ok) {
            setErrorMessage(data.detail);  
        } else {
          navigate("/login");  
        }
      };
    
      const handleSubmit = (e) => {
        e.preventDefault();
        submitRegister();
      };

    return (
        <div className='h-screen flex justify-center items-center  bg-gray-100 shadow-md  dark:bg-gray-900 '>
            <Card className='w-[460px]'>

            
                <CardHeader className="space-y-1  dark:text-white">
                <ModeToggle/>
                    <CardTitle className="text-2xl">Create an account</CardTitle>
                    <CardDescription>
                        Enter your detials below to create your account
                    </CardDescription>
                </CardHeader>

                <CardContent as="form" onSubmit={handleSubmit} className="grid gap-4">
                    <div className="grid gap-2">
                        <Label htmlFor="username">Username</Label>
                        <Input id="username" name="username" type="text" placeholder="someone" required value={username}
              onChange={(e) => setUsername(e.target.value)}  />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="email">Email</Label>
                        <Input id="email" name="email" type="email"  placeholder="example@gmail.com" required  value={email}
              onChange={(e) => setEmail(e.target.value)} />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="password">Password</Label>
                        <Input id="password" type="password"  placeholder="keep it secret" value={password}
              onChange={(e) => setPassword(e.target.value)}  />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="balance">balance</Label>
                        <Input id="balance" name="balance" type="number" placeholder="no limit" required value={balance}
              onChange={(e) => setBalance(e.target.value)}  />
                    </div>
                </CardContent>


                <CardFooter className="flex flex-col gap-4">
                <Button type="submit"  onClick={handleSubmit} className="w-full">Create account</Button>
        <Button
            onClick={() => navigate("/login", { replace: true })}
            width="100%"
            colorScheme="gray"
            variant="outline"
            mt={6}
            className="w-full text-gray-500 border-gray-500">
            Login
          </Button>
      </CardFooter>
            </Card>
        </div>
    );
}

export default Register;
