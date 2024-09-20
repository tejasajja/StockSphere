import  { useState } from 'react';

import ErrorMessage from '@/components/ErrorMessage';
// import { Icons } from "@/components/ui/icons";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from "@/components/ui/card";
  
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";
import { useLocalState } from '@/utils/usingLocalStorage';
import { ModeToggle } from '@/components/mode-toggle';



function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const[jwt, setJwt]= useLocalState("","jwt");



    const submitLogin = async () => {
        const requestOptions = {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: JSON.stringify(
            `grant_type=&username=${email}&password=${password}&scope=&client_id=&client_secret=`
          ),
        };
    
        const response = await fetch("http://localhost:8000/api/auth/login", requestOptions);
        const data = await response.json();
    
        if (!response.ok) {
            setErrorMessage(data.detail);
        } else {
          console.log(data.access_token)
          localStorage.setItem("awesomeLeadsToken", data.access_token);
          setJwt(data.access_token);
          window.location.href="stockdashboard";

        }
        
      };
    
      const handleSubmit = (e) => {
        e.preventDefault();
        submitLogin();
      };

    // const[jwt, setJwt]= useLocalState("","jwt");

    
    return (
        <div className='h-screen flex justify-center items-center  bg-gray-100 shadow-md  dark:bg-gray-900 '>
      <Card className='w-[460px] mx-auto  dark:text-white'>
      

      <CardHeader className="space-y-1">
      <ModeToggle/>
        <CardTitle className="text-2xl">Login</CardTitle>
        <CardDescription>
          Enter your username and password below to Login
        </CardDescription>
      </CardHeader>


      <CardContent className="grid gap-4">
        <div className="grid gap-2 item-start space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input id="username" type="text" placeholder="tsajja" value={email}
    onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="grid gap-2 item-start space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password"  placeholder="keep it secret" value={password}
              onChange={(e) => setPassword(e.target.value)}  />
        </div>
        {errorMessage && (
      <ErrorMessage message={errorMessage} />
    )}
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        <Button className="w-full" type="submit" onClick={handleSubmit} >Login</Button>
        <Button
            onClick={() => navigate("/register", { replace: true })}
            width="100%"
            colorScheme="gray"
            variant="outline"
            mt={6}
            className="w-full text-gray-500 border-gray-500">
            Register
          </Button>
      </CardFooter>
    </Card>
        </div>
    );
}

export default Login;